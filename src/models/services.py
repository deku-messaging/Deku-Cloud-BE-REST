"""Service Handler"""

import logging

from werkzeug.exceptions import Unauthorized

from twilio.rest import Client

from src.models.rabbitmq import RabbitMQModel
from src.models.logs import LogModel
from src.std_carrier_lib.helpers import CarrierInformation

logger = logging.getLogger(__name__)


class ServerModel:
    """Handler definition"""

    def __init__(self, service: str) -> None:
        self.carrier_information = CarrierInformation
        self.rabbitmq = RabbitMQModel
        self.log = LogModel
        self.twilio = Client
        self.service = service

    def get_service_name(self, pid: str, identifier: str = None) -> str:
        """Get driver name from identifier

        Keyword arguments:
        pid -- project's ID
        identifier -- phone number

        return: str
        """

        ci_ = self.carrier_information()

        try:
            if self.service.lower() in ["sms"]:
                country_name = ci_.get_country(phone_number=identifier)
                service_provider = ci_.get_operator_name(phone_number=identifier)
                service_name = f"{pid}_{country_name}_{service_provider}"

            logger.info("[X] Successfully got service name")

            return service_name

        except Exception as error:
            raise error

    def publish(
        self,
        content: str,
        identifier: str,
        pid: str,
        user: object,
    ) -> None:
        """Publish content to service

        Keyword arguments:
        user -- user's object
        content -- content to be published
        identifier -- phone_number |
        pid -- project_id

        return: None
        """

        log = self.log()
        rabbitmq = self.rabbitmq(vhost=user.account_sid)
        service_name = self.get_service_name(pid=pid, identifier=identifier)
        twilio = (
            user.twilio_account_sid
            and user.twilio_service_sid
            and user.twilio_auth_token
        )

        try:
            if self.service.lower() in ["sms"]:
                body = {"text": content, "number": identifier}

                if not rabbitmq.find_one_queue(name=service_name):
                    if twilio:
                        try:
                            client = self.twilio(
                                user.twilio_account_sid, user.twilio_auth_token
                            )
                            message = client.messages.create(
                                body=content,
                                messaging_service_sid=user.twilio_service_sid,
                                to=identifier,
                            )

                        except Exception as error:
                            raise Unauthorized(error) from error

                        logger.info("[x] Successfully requested with twilio")

                        channel = "twilio"
                        sid = message.sid
                        from_ = message.from_
                        direction = message.direction
                        status = message.status
                        reason = message.error_message
                        date_created = message.date_created
                        to_ = message.to
                        body = message.body

                        log.create(
                            sid=sid,
                            service=self.service.lower(),
                            pid=pid,
                            to_=to_,
                            from_=from_,
                            channel=channel,
                            user_id=user.id,
                            direction=direction,
                            status=status,
                            reason=reason,
                        )

                        return {
                            "sid": sid,
                            "created_at": date_created,
                            "direction": direction,
                            "status": status,
                            "from": from_,
                            "to": to_,
                            "channel": channel,
                            "body": body,
                            "reason": reason,
                        }

                    logger.info("[x] Successfully cancelled sms")

                    channel = None
                    sid = None
                    from_ = None
                    direction = "outbound-api"
                    status = "cancelled"
                    reason = "No available channel. Start a Deku SMS client or provide your Twilio messaging credentials."
                    date_created = None
                    to_ = identifier
                    body = content

                    log_ = log.create(
                        serivce_name=service_name,
                        service=self.service.lower(),
                        pid=pid,
                        to_=to_,
                        user_id=user.id,
                        direction=direction,
                        status=status,
                        reason=reason,
                    )

                    return {
                        "sid": log_.sid,
                        "created_at": log_.created_at,
                        "direction": direction,
                        "status": status,
                        "from": from_,
                        "to": to_,
                        "channel": channel,
                        "body": body,
                        "reason": reason,
                    }

                rabbitmq.publish(
                    body=body,
                    routing_key=service_name,
                    exchange=pid,
                    vhost=user.account_sid,
                )

                logger.info("[x] Successfully requested sms")

                channel = "deku_client"
                sid = None
                from_ = None
                direction = "outbound-api"
                status = "requested"
                reason = None
                date_created = None
                to_ = identifier
                body = content

                log_ = log.create(
                    serivce_name=service_name,
                    service=self.service.lower(),
                    pid=pid,
                    to_=to_,
                    user_id=user.id,
                    direction=direction,
                    status=status,
                    reason=reason,
                )

                return {
                    "sid": log_.sid,
                    "created_at": log_.created_at,
                    "direction": direction,
                    "status": status,
                    "from": from_,
                    "to": to_,
                    "channel": channel,
                    "body": body,
                    "reason": reason,
                }

        except Exception as error:
            raise error
