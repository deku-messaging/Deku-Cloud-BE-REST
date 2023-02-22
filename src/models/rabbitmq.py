"""RabbitMQ Handler"""

import logging
import requests

from settings import Configurations

logger = logging.getLogger(__name__)

rabbitmq_user = Configurations.RABBITMQ_USER
rabbitmq_password = Configurations.RABBITMQ_PASSWORD
rabbitmq_host = Configurations.RABBITMQ_HOST
rabbitmq_management_port = Configurations.RABBITMQ_MANAGEMENT_PORT
rabbitmq_ssl_management_port = Configurations.RABBITMQ_MANAGEMENT_PORT_SSL
rabbitmq_ssl_active = Configurations.RABBITMQ_SSL_ACTIVE
rabbitmq_active_port = (
    rabbitmq_ssl_management_port if rabbitmq_ssl_active else rabbitmq_management_port
)
RABBITMQ_URL_PROTOCOL = "https" if rabbitmq_ssl_active else "http"


class RabbitMQModel:
    """Handler definition"""

    def __init__(self):
        self.rabbitmq_req_url = (
            f"{RABBITMQ_URL_PROTOCOL}://{rabbitmq_host}:{rabbitmq_active_port}"
        )

    def add_user(
        self,
        username: str,
        password: str,
    ) -> None:
        """Add user to rabbitmq.

        Keyword arguments:
        username -- user's username (unique)
        password -- user's password

        return: None
        """

        try:
            add_vhost_url = f"{self.rabbitmq_req_url}/api/vhosts/{username}"
            add_user_url = f"{self.rabbitmq_req_url}/api/users/{username}"
            set_permissions_url = (
                f"{self.rabbitmq_req_url}/api/permissions/{username}/{username}"
            )

            add_user_data = {"password": password, "tags": "management"}
            set_permissions_data = {"configure": ".*", "write": ".*", "read": ".*"}

            add_vhost_response = requests.put(
                url=add_vhost_url,
                auth=(rabbitmq_user, rabbitmq_password),
            )

            if add_vhost_response.status_code in [201, 204]:
                logger.debug("[*] New vhost added")

                add_user_response = requests.put(
                    url=add_user_url,
                    json=add_user_data,
                    auth=(rabbitmq_user, rabbitmq_password),
                )

                if add_user_response.status_code in [201, 204]:
                    logger.debug("[*] New user added")
                    logger.debug("[*] User tag set")

                    set_permissions_response = requests.put(
                        url=set_permissions_url,
                        json=set_permissions_data,
                        auth=(rabbitmq_user, rabbitmq_password),
                    )

                    if set_permissions_response.status_code in [201, 204]:
                        logger.debug("[*] User privilege set")
                        return None

                    logger.error("[!] Failed to set user privilege")
                    set_permissions_response.raise_for_status()

                else:
                    logger.error("[!] Failed to add new user")
                    add_user_response.raise_for_status()

            else:
                logger.error("[!] Failed to add new vhost")
                add_user_response.raise_for_status()

        except Exception as error:
            raise error
        
    def add_exchange(
        self,
        vhost: str,
        name: str,
    ) -> None:
        """Add exchange to rabbitmq.

        Keyword arguments:
        vhost -- vhost name
        name -- exchange name

        return: None
        """

        try:
            add_exchange_url = f"{self.rabbitmq_req_url}/api/exchanges/{vhost}/{name}"

            add_exchange_data = {
                "type": "topic",
                "auto_delete":False,
                "durable":True,
                "internal":False,
                "arguments":{}
            }

            add_exchange_response = requests.put(
                url=add_exchange_url,
                json=add_exchange_data,
                auth=(rabbitmq_user, rabbitmq_password),
            )

            if add_exchange_response.status_code in [201, 204]:
                logger.debug("[*] New exchange added")
                return None

            else:
                logger.error("[!] Failed to add new exchange")
                add_exchange_response.raise_for_status()

        except Exception as error:
            raise error
        
