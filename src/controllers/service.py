"""Controller Functions for Service Operations"""

import logging

import phonenumbers

from werkzeug.exceptions import BadRequest

from twilio.rest import Client as Twilio
from twilio.base.exceptions import TwilioRestException

from playhouse.shortcuts import model_to_dict

from src.utils import rabbitmq, carrier_services
from src.utils.std_carrier_lib.helpers import InvalidPhoneNUmber
from src.orm.peewee.handlers.log import LogHandler

logger = logging.getLogger(__name__)


def create_log(**kwargs):
    """
    Create a log entry with the provided information.

    :param kwargs: Keyword arguments for the log entry.
    :return: The created log entry.
    """
    log_handler = LogHandler()

    return model_to_dict(log_handler.create_log(**kwargs), recurse=False)


def handle_invalid_phone_number(service_id, project_reference, phone_number, user, sid):
    """
    Handle the case of an invalid phone number.

    :param service_id: ID of the service.
    :param project_reference: Reference to the project.
    :param phone_number: Invalid phone number.
    :param user: User information.
    :raises: InvalidPhoneNumber
    """
    error_message = f"Invalid phone number: '{phone_number}'"

    create_log(
        user_id=user.get("id"),
        service_id=service_id.lower(),
        project_reference=project_reference,
        status="failed",
        reason=error_message,
        to_=phone_number,
        sid=sid,
    )

    raise InvalidPhoneNUmber(error_message)


def handle_number_parse_exception(
    service_id, project_reference, phone_number, user, error, sid
):
    """
    Handle a number parse exception.

    :param service_id: ID of the service.
    :param project_reference: Reference to the project.
    :param phone_number: Phone number that caused the exception.
    :param user: User information.
    :param error: Number parse exception object.
    """
    error_message = str(error)

    create_log(
        user_id=user.get("id"),
        service_id=service_id.lower(),
        project_reference=project_reference,
        status="failed",
        reason=error_message,
        to_=phone_number,
        sid=sid,
    )

    raise error


def handle_no_client_exception(
    service_name, service_id, project_reference, phone_number, user, sid
):
    """
    Handle the case where no client is available for the service.

    :param service_name: Name of the service.
    :param service_id: ID of the service.
    :param project_reference: Reference to the project.
    :param phone_number: Recipient's phone number.
    :param user: User information.
    :return: The created log entry.
    """

    return create_log(
        user_id=user.get("id"),
        service_id=service_id.lower(),
        project_reference=project_reference,
        service_name=service_name,
        direction="outbound-api",
        status="failed",
        reason="No available channel. Start a Deku SMS client or provide your Twilio messaging credentials.",
        to_=phone_number,
        sid=sid,
    )


def handle_twilio_rest_exception(
    service_id, project_reference, phone_number, user, error, sid
):
    """
    Handle a TwilioRestException.

    :param service_id: ID of the service.
    :param project_reference: Reference to the project.
    :param phone_number: Phone number associated with the exception.
    :param user: User information.
    :param error: TwilioRestException object.
    :raises: TwilioRestException
    """

    logger.error("Failed to publish with Twilio client")

    create_log(
        user_id=user.get("id"),
        service_id=service_id.lower(),
        project_reference=project_reference,
        channel="twilio",
        status="failed",
        reason=error.msg,
        to_=phone_number,
        sid=sid,
    )

    raise error


def handle_generic_exception(
    service_id, project_reference, phone_number, user, error, sid
):
    """
    Handle a generic exception.

    :param service_id: ID of the service.
    :param project_reference: Reference to the project.
    :param phone_number: Phone number associated with the exception.
    :param user: User information.
    :param error: The exception object.
    """
    error_message = "Oops! Something went wrong. Please try again. If the issue persists, please contact the developers."
    create_log(
        user_id=user.get("id"),
        service_id=service_id.lower(),
        project_reference=project_reference,
        status="failed",
        reason=error_message,
        to_=phone_number,
        sid=sid,
    )
    raise error


def publish_with_twilio(
    twilio_client, service_id, project_reference, content, phone_number, user
):
    """
    Publish a message using the Twilio client.

    :param twilio_client: Twilio client object.
    :param service_id: ID of the service.
    :param project_reference: Reference to the project.
    :param content: Content of the message.
    :param phone_number: Recipient's phone number.
    :param user: User information.
    :return: The created log entry.
    :raises: TwilioRestException
    """
    message = twilio_client.messages.create(
        body=content,
        messaging_service_sid=user.get("twilio_service_sid"),
        to=phone_number,
    )

    logger.info("Successfully published with Twilio client")

    return create_log(
        user_id=user.get("id"),
        service_id=service_id.lower(),
        project_reference=project_reference,
        channel="twilio",
        sid=message.sid,
        from_=message.from_,
        direction=message.direction,
        status=message.status,
        reason=message.error_message,
        created_at=message.date_created,
        to_=message.to,
        body=message.body,
    )


def publish_with_deku_client(
    service_name, service_id, project_reference, content, phone_number, user, sid
):
    """
    Publish a message using the Deku client.

    :param service_name: Name of the Deku service.
    :param service_id: ID of the service.
    :param project_reference: Reference to the project.
    :param content: Content of the message.
    :param phone_number: Recipient's phone number.
    :param user: User information.
    :return: The created log entry.
    """

    log_handler = LogHandler()

    new_log = log_handler.create_log(
        user_id=user.get("id"),
        service_id=service_id.lower(),
        project_reference=project_reference,
        channel="deku_client",
        service_name=service_name,
        direction="outbound-api",
        status="",
        to_=phone_number,
        sid=sid,
    )

    body = {"text": content, "to": phone_number, "id": new_log.id, "sid": sid}

    try:
        rabbitmq.publish_to_exchange(
            body=body,
            routing_key=service_name.replace("_", "."),
            exchange=project_reference,
            virtual_host=user.get("account_sid"),
        )
    except Exception:
        new_log.delete_instance()
        raise

    logger.info("Successfully published with Deku client")

    new_log.status = "requested"
    new_log.save()

    return model_to_dict(new_log, recurse=False)


def publish_to_service(
    service_id, content, project_reference, user, phone_number=None, sid=None
):
    """
    Publish a message to the specified service.

    :param service_id: ID of the service.
    :param content: Content of the message.
    :param project_reference: Reference to the project.
    :param user: User information.
    :param phone_number: Recipient's phone number.
    :return: The created log entry.
    :raises: InvalidPhoneNumber, NumberParseException, BadRequest, Exception
    """
    twilio_account_sid = user.get("twilio_account_sid")
    twilio_auth_token = user.get("twilio_auth_token")
    account_sid = user.get("account_sid")

    has_twilio = all((twilio_account_sid, twilio_auth_token))

    try:
        service_name = carrier_services.get_service_name(
            service_id=service_id,
            project_reference=project_reference,
            phone_number=phone_number,
        )

        if service_name:
            if not rabbitmq.get_queue_by_name(
                name=service_name, virtual_host=account_sid
            ):
                if has_twilio:
                    twilio_client = Twilio(
                        username=twilio_account_sid, password=twilio_auth_token
                    )
                    return publish_with_twilio(
                        twilio_client=twilio_client,
                        service_id=service_id,
                        project_reference=project_reference,
                        content=content,
                        phone_number=phone_number,
                        user=user,
                    )

                logger.info("Failed to publish SMS")
                return handle_no_client_exception(
                    service_name=service_name,
                    service_id=service_id,
                    project_reference=project_reference,
                    phone_number=phone_number,
                    user=user,
                    sid=sid,
                )

            return publish_with_deku_client(
                service_name=service_name,
                service_id=service_id,
                project_reference=project_reference,
                content=content,
                phone_number=phone_number,
                user=user,
                sid=sid,
            )

        logger.error("Unsupported service_id '%s'", service_id)
        raise BadRequest(f"Unsupported service_id {service_id}")

    except InvalidPhoneNUmber:
        handle_invalid_phone_number(
            service_id=service_id,
            project_reference=project_reference,
            phone_number=phone_number,
            user=user,
            sid=sid,
        )
    except phonenumbers.NumberParseException as error:
        handle_number_parse_exception(
            service_id=service_id,
            project_reference=project_reference,
            phone_number=phone_number,
            user=user,
            error=error,
            sid=sid,
        )
    except TwilioRestException as error:
        handle_twilio_rest_exception(
            service_id=service_id,
            project_reference=project_reference,
            phone_number=phone_number,
            user=user,
            error=error,
            sid=sid,
        )
    except (Exception, BadRequest) as error:
        handle_generic_exception(
            service_id=service_id,
            project_reference=project_reference,
            phone_number=phone_number,
            user=user,
            error=error,
            sid=sid,
        )
