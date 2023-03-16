"""RabbitMQ Handler"""

import ssl
import logging
import json

import requests
import pika

from settings import Configurations

logger = logging.getLogger(__name__)

rabbitmq_user = Configurations.RABBITMQ_USER
rabbitmq_password = Configurations.RABBITMQ_PASSWORD
rabbitmq_host = Configurations.RABBITMQ_HOST
rabbitmq_management_port = Configurations.RABBITMQ_MANAGEMENT_PORT
rabbitmq_server_port = Configurations.RABBITMQ_SERVER_PORT
rabbitmq_ssl_management_port = Configurations.RABBITMQ_MANAGEMENT_PORT_SSL
rabbitmq_ssl_active = Configurations.RABBITMQ_SSL_ACTIVE
rabbitmq_ssl_server_port = Configurations.RABBITMQ_SERVER_PORT_SSL
rabbitmq_active_port = (
    rabbitmq_ssl_management_port if rabbitmq_ssl_active else rabbitmq_management_port
)
RABBITMQ_URL_PROTOCOL = "https" if rabbitmq_ssl_active else "http"
rabbitmq_ssl_cacert = Configurations.SSL_PEM
rabbitmq_ssl_crt = Configurations.SSL_CERTIFICATE
rabbitmq_ssl_key = Configurations.SSL_KEY


class RabbitMQModel:
    """Handler definition"""

    def __init__(self, vhost: str) -> None:
        self.rabbitmq_req_url = (
            f"{RABBITMQ_URL_PROTOCOL}://{rabbitmq_host}:{rabbitmq_active_port}"
        )
        self.vhost = vhost

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
        name: str,
    ) -> None:
        """Add exchange to rabbitmq.

        Keyword arguments:
        name -- exchange name

        return: None
        """

        try:
            add_exchange_url = (
                f"{self.rabbitmq_req_url}/api/exchanges/{self.vhost}/{name}"
            )

            add_exchange_data = {
                "type": "topic",
                "auto_delete": False,
                "durable": True,
                "internal": False,
                "arguments": {},
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

    def find_one_queue(self, name: str) -> dict:
        """Find a single queue

        Keyword arguments:
        name -- queue name

        return: dict
        """

        try:
            find_one_queue_url = (
                f"{self.rabbitmq_req_url}/api/queues/{self.vhost}/{name}"
            )

            find_one_queue_response = requests.get(
                url=find_one_queue_url,
                auth=(rabbitmq_user, rabbitmq_password),
            )

            if find_one_queue_response.status_code in [200]:
                logger.debug("[*] Found queue: %s", name)
                return find_one_queue_response.json

            elif find_one_queue_response.status_code in [404]:
                logger.debug("[*] No queue: %s", name)
                return None

            else:
                logger.error("[!] Failed to find queue")
                find_one_queue_response.raise_for_status()

        except Exception as error:
            raise error

    def publish(self, routing_key: str, body: dict, exchange: str, vhost: str) -> None:
        """Publish to a single queue

        Keyword arguments:
        routing_key -- queue_name | binding_key | routing_key
        body -- content to be published
        exchange -- exchange name

        return: None
        """

        try:
            credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)

            if rabbitmq_ssl_active:
                context = ssl.create_default_context(cafile=rabbitmq_ssl_cacert)
                context.load_cert_chain(rabbitmq_ssl_crt, rabbitmq_ssl_key)

                ssl_options = pika.SSLOptions(context)
                conn_params = pika.ConnectionParameters(
                    host=rabbitmq_host,
                    port=rabbitmq_ssl_server_port,
                    ssl_options=ssl_options,
                    virtual_host=vhost,
                    credentials=credentials,
                )
            else:
                conn_params = pika.ConnectionParameters(
                    host=rabbitmq_host,
                    port=rabbitmq_server_port,
                    virtual_host=vhost,
                    credentials=credentials,
                )

            connection = pika.BlockingConnection(conn_params)

            channel = connection.channel()

            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(body),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ),
            )

        except Exception as error:
            raise error

        finally:
            connection.close()
