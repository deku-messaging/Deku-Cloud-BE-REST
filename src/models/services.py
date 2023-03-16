"""Service Handler"""

import logging

from werkzeug.exceptions import Unauthorized

from twilio.rest import Client

from src.models.rabbitmq import RabbitMQModel
from src.std_carrier_lib.helpers import CarrierInformation

logger = logging.getLogger(__name__)


class ServerModel:
    """Handler definition"""

    def __init__(self, service: str) -> None:
        self.carrier_information = CarrierInformation
        self.rabbitmq = RabbitMQModel
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

        except Exception as error:
            raise error

        else:
            logger.info("[X] Successfully got service name")

            return service_name

    def publish(
        self,
        content: str,
        identifier: str,
        pid: str,
        account_sid: str,
        twilio_service_sid: str = None,
        twilio_account_sid: str = None,
        twilio_auth_token: str = None,
    ) -> None:
        """Publish content to service

        Keyword arguments:
        account_sid -- user's account sid
        content -- content to be published
        identifier -- phone_number |
        pid -- project_id
        twilio_service_sid -- user's service_sid
        twilio_account_sid -- user's account_sid
        twilio_auth_token -- user's auth_token

        return: None
        """

        rabbitmq = self.rabbitmq(vhost=account_sid)
        service_name = self.get_service_name(pid=pid, identifier=identifier)
        twilio = twilio_account_sid and twilio_service_sid and twilio_auth_token

        try:
            if self.service.lower() in ["sms"]:
                body = {"text": content, "number": identifier}

                if not rabbitmq.find_one_queue(name=service_name):
                    if twilio:
                        try:
                            client = self.twilio(twilio_account_sid, twilio_auth_token)
                            message = client.messages.create(
                                body=content,
                                messaging_service_sid=twilio_service_sid,
                                to=identifier,
                            )

                        except Exception as error:
                            raise Unauthorized(error) from error

                        logger.info("[x] Successfully requested with twilio")
                        return {"message_sid": message.sid}

                rabbitmq.publish(
                    body=body, routing_key=service_name, exchange=pid, vhost=account_sid
                )

                print(pid, body, service_name, account_sid)
                logger.info("[x] Successfully requested sms")

        except Exception as error:
            raise error
