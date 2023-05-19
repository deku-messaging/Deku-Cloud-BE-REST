"""Controller Functions for Service Operations"""

import logging

from werkzeug.exceptions import BadRequest

from twilio.rest import Client as Twilio
from twilio.base.exceptions import TwilioRestException

from playhouse.shortcuts import model_to_dict

from src.utils import rabbitmq, carrier_services
from src.orm.peewee.handlers.log import LogHandler

logger = logging.getLogger(__name__)


def publish_to_service(
    service_id: str,
    content: str,
    project_reference: str,
    user: dict,
    phone_number: str = None,
) -> bool:
    """
    Publish content to a service.

    :param service_id: str - The unique identifier for the service.
    :param project_reference: str - A unique reference for the project.
    :param content: str - content to be published.
    :param phone_number: str - The phone number to send the message to (for SMS services only).
    :param user: dict - The user associated with the request.

    :return: dict - A dictionary representing the log entry for the published content.
    """

    log_handler = LogHandler()

    service_name = carrier_services.get_service_name(
        service_id=service_id,
        project_reference=project_reference,
        phone_number=phone_number,
    )

    twilio_account_sid = user.get("twilio_account_sid")
    twilio_service_sid = user.get("twilio_service_sid")
    twilio_auth_token = user.get("twilio_auth_token")
    account_sid = user.get("account_sid")
    user_id = user.get("id")

    has_twilio = all((twilio_account_sid, twilio_service_sid, twilio_auth_token))

    if service_id.lower() == "sms":
        if not rabbitmq.get_queue_by_name(name=service_name, virtual_host=account_sid):
            if has_twilio:
                twilio_client = Twilio(
                    username=twilio_account_sid, password=twilio_auth_token
                )

                try:
                    message = twilio_client.messages.create(
                        body=content,
                        messaging_service_sid=twilio_service_sid,
                        to=phone_number,
                    )
                except TwilioRestException as error:
                    logger.error("Failed publised with twilio client")

                    log_data = {
                        "channel": "twilio",
                        "status": "failed",
                        "reason": error.msg,
                        "to_": phone_number,
                        "body": content,
                    }

                    new_log = log_handler.create_log(
                        user_id=user_id,
                        service_id=service_id.lower(),
                        project_reference=project_reference,
                        **log_data,
                    )

                    raise error

                logger.info("Successfully publised with twilio client")

                log_data = {
                    "channel": "twilio",
                    "sid": message.sid,
                    "from_": message.from_,
                    "direction": message.direction,
                    "status": message.status,
                    "reason": message.error_message,
                    "created_at": message.date_created,
                    "to_": message.to,
                    "body": message.body,
                }

                new_log = log_handler.create_log(
                    user_id=user_id,
                    service_id=service_id.lower(),
                    project_reference=project_reference,
                    **log_data,
                )

            else:
                logger.info("Failed to publish sms")

                log_data = {
                    "service_name": service_name,
                    "direction": "outbound-api",
                    "status": "failed",
                    "reason": "No available channel. Start a Deku SMS client or provide your Twilio messaging credentials.",
                    "to_": phone_number,
                    "body": content,
                }

                new_log = log_handler.create_log(
                    user_id=user_id,
                    service_id=service_id.lower(),
                    project_reference=project_reference,
                    **log_data,
                )

        else:
            body = {"text": content, "number": phone_number}

            rabbitmq.publish_to_exchange(
                body=body,
                routing_key=service_name,
                exchange=project_reference,
                virtual_host=account_sid,
            )

            logger.info("Successfully publised with deku client")

            log_data = {
                "channel": "deku_client",
                "service_name": service_name,
                "direction": "outbound-api",
                "status": "requested",
                "to_": phone_number,
                "body": content,
            }

            new_log = log_handler.create_log(
                user_id=user_id,
                service_id=service_id.lower(),
                project_reference=project_reference,
                **log_data,
            )

        return model_to_dict(new_log, recurse=False)

    error_message = f"Unsupported service_id '{service_id}'"
    logger.error(error_message)
    raise BadRequest(error_message)
