"""RabbitMQ Utils"""

import ssl
import logging
import json

import requests
import pika

from settings import Configurations

logger = logging.getLogger(__name__)

config = Configurations
rabbitmq_user, rabbitmq_password, rabbitmq_host = (
    config.RABBITMQ_USER,
    config.RABBITMQ_PASSWORD,
    config.RABBITMQ_HOST,
)
rabbitmq_management_port, rabbitmq_server_port = (
    config.RABBITMQ_MANAGEMENT_PORT,
    config.RABBITMQ_SERVER_PORT,
)
rabbitmq_ssl_management_port, rabbitmq_ssl_server_port = (
    config.RABBITMQ_MANAGEMENT_PORT_SSL,
    config.RABBITMQ_SERVER_PORT_SSL,
)
rabbitmq_ssl_active = config.RABBITMQ_SSL_ACTIVE
rabbitmq_ssl_cacert, rabbitmq_ssl_crt, rabbitmq_ssl_key = (
    config.SSL_PEM,
    config.SSL_CERTIFICATE,
    config.SSL_KEY,
)

rabbitmq_active_port = (
    rabbitmq_ssl_management_port if rabbitmq_ssl_active else rabbitmq_management_port
)
RABBITMQ_URL_PROTOCOL = "https" if rabbitmq_ssl_active else "http"

BASE_URL = f"{RABBITMQ_URL_PROTOCOL}://{rabbitmq_host}:{rabbitmq_active_port}/api"
AUTH = (rabbitmq_user, rabbitmq_password)


def create_virtual_host(name: str, **kwargs) -> bool:
    """
    Create a virtual host with the specified name.

    :param name: str - The name of the virtual host to create.
    :param kwargs: dict - Additional arguments to include in the request payload.

    :return :bool - True if the virtual host was created successfully.
    """
    url = f"{BASE_URL}/vhosts/{name}"
    data = {**kwargs}

    try:
        response = requests.put(url=url, json=data, auth=AUTH)
        response.raise_for_status()  # raise HTTPError for 4xx and 5xx errors
    except requests.exceptions.HTTPError as error:
        logger.error(
            "Failed to create virtual host '%s': %s", name, error.response.text
        )
        raise error

    logger.info("Successfully created virtual host '%s'", name)
    return True


def delete_virtual_host(name: str, **kwargs) -> bool:
    """
    Delete a virtual host with the specified name.

    :param name: str - The name of the virtual host to delete.
    :param kwargs: dict - Additional arguments to include in the request payload.

    :return :bool - True if the virtual host was deleted successfully.
    """
    url = f"{BASE_URL}/vhosts/{name}"
    data = {**kwargs}

    try:
        response = requests.delete(url=url, json=data, auth=AUTH)
        response.raise_for_status()  # raise HTTPError for 4xx and 5xx errors
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            logger.warning("Virtual Host '%s' not found", name)
            return None
        logger.error(
            "Failed to delete virtual host '%s': %s", name, error.response.text
        )
        raise error

    logger.info("Successfully deleted virtual host '%s'", name)
    return True


def create_user(username: str, password: str, **kwargs) -> bool:
    """
    Creates a new user with the specified username and password.

    :param username: str - The username of the user to be created.
    :param password: str - The password for the user to be created.
    :param kwargs: dict - Additional arguments to include in the request payload.

    :return: bool - True if the user was created successfully, False otherwise.
    """
    url = f"{BASE_URL}/users/{username}"
    data = {"password": password, **kwargs}

    try:
        response = requests.put(url=url, json=data, auth=AUTH)
        response.raise_for_status()  # raise HTTPError for 4xx and 5xx errors
    except requests.exceptions.HTTPError as error:
        logger.error("Failed to create user '%s': %s", username, error.response.text)
        raise error

    logger.info("Successfully created user '%s'", username)
    return True


def delete_user(username: str, **kwargs) -> bool:
    """
    Deletes a user with the specified username.

    :param username: str - The username of the user to be deleted.
    :param kwargs: dict - Additional arguments to include in the request payload.

    :return: bool - True if the user was deleted successfully, False otherwise.
    """
    url = f"{BASE_URL}/users/{username}"
    data = {**kwargs}

    try:
        response = requests.delete(url=url, json=data, auth=AUTH)
        response.raise_for_status()  # raise HTTPError for 4xx and 5xx errors
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            logger.warning("User '%s' not found", username)
            return None
        logger.error("Failed to delete user '%s': %s", username, error.response.text)
        raise error

    logger.info("Successfully deleted user '%s'", username)
    return True


def set_permissions(
    configure: str, write: str, read: str, username: str, virtual_host: str, **kwargs
) -> bool:
    """
    Set the permissions for a user on a virtual host.

    :param configure: str - The configure permission for the user, e.g. ".*" or "^amq\."
    :param write: str - The write permission for the user, e.g. ".*" or "^myqueue$"
    :param read: str - The read permission for the user, e.g. ".*" or "^myqueue$"
    :param username: str - The name of the user to set the permissions for.
    :param virtual_host: str - The name of the virtual host to set the permissions on.
    :param kwargs: dict - Additional arguments to include in the request payload.

    :return: bool - True if the permissions were set successfully, otherwise False.
    """
    url = f"{BASE_URL}/permissions/{virtual_host}/{username}"
    data = {"configure": configure, "write": write, "read": read, **kwargs}

    try:
        response = requests.put(url=url, json=data, auth=AUTH)
        response.raise_for_status()  # raise HTTPError for 4xx and 5xx errors
    except requests.exceptions.HTTPError as error:
        logger.error("Failed to set permissions '%s': %s", data, error.response.text)
        raise error

    logger.info("Successfully set permissions '%s'", username)
    return True


def create_exchange(virtual_host: str, name: str, **kwargs) -> bool:
    """
    Create an exchange with the specified name and arguments on the specified virtual host.

    :param virtual_host: str - The name of the virtual host on which to create the exchange.
    :param name: str - The name of the exchange to create.
    :param kwargs: dict - Additional arguments to include in the request payload.

    :return: bool - True if the exchange was created successfully, otherwise False.
    """
    url = f"{BASE_URL}/exchanges/{virtual_host}/{name}"
    data = {**kwargs}

    try:
        response = requests.put(url=url, json=data, auth=AUTH)
        response.raise_for_status()  # raise HTTPError for 4xx and 5xx errors
    except requests.exceptions.HTTPError as error:
        logger.error("Failed to create exchange '%s': %s", name, error.response.text)
        raise error

    logger.info("Successfully created exchange '%s'", name)
    return True


def get_exhange_by_name(name: str, virtual_host: str) -> dict:
    """
    Retrieve a exchange by its name and virtual host.

    :param name: str - The name of the exchange to retrieve.
    :param virtual_host: str - The name of the virtual host that the exchange belongs to.

    :return: dict - A dictionary representing the exchange's properties, or None if the exchange does not exist.
    """
    url = f"{BASE_URL}/exchanges/{virtual_host}/{name}"

    try:
        response = requests.get(url=url, auth=AUTH)
        response.raise_for_status()  # raise HTTPError for 4xx and 5xx errors
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            logger.warning(
                "Exchange '%s' not found in virtual host '%s'", name, virtual_host
            )
            return None
        logger.error("Failed to retrieve exchange '%s': %s", name, error.response.text)
        raise error

    logger.info("Successfully retrieved exchange '%s'", name)
    return response.json()


def delete_exchange(virtual_host: str, name: str, **kwargs) -> bool:
    """
    Delete an exchange with the specified name and arguments on the specified virtual host.

    :param virtual_host: str - The name of the virtual host on which to delete the exchange.
    :param name: str - The name of the exchange to delete.
    :param kwargs: dict - Additional arguments to include in the request payload.

    :return: bool - True if the exchange was deleted successfully, otherwise False.
    """
    url = f"{BASE_URL}/exchanges/{virtual_host}/{name}"
    data = {**kwargs}

    try:
        response = requests.delete(url=url, json=data, auth=AUTH)
        response.raise_for_status()  # raise HTTPError for 4xx and 5xx errors
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            logger.warning(
                "Exchange '%s' not found in virtual host '%s'", name, virtual_host
            )
            return None
        logger.error("Failed to delete exchange '%s': %s", name, error.response.text)
        raise error

    logger.info("Successfully deleted exchange '%s'", name)
    return True


def get_queue_by_name(name: str, virtual_host: str) -> dict:
    """
    Retrieve a queue by its name and virtual host.

    :param name: str - The name of the queue to retrieve.
    :param virtual_host: str - The name of the virtual host that the queue belongs to.

    :return: dict - A dictionary representing the queue's properties, or None if the queue does not exist.
    """
    url = f"{BASE_URL}/queues/{virtual_host}/{name}"

    try:
        response = requests.get(url=url, auth=AUTH)
        response.raise_for_status()  # raise HTTPError for 4xx and 5xx errors
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 404:
            logger.warning(
                "Queue '%s' not found in virtual host '%s'", name, virtual_host
            )
            return None
        logger.error("Failed to retrieve queue '%s': %s", name, error.response.text)
        raise error

    logger.info("Successfully retrieved queue '%s'", name)
    return response.json()


def publish_to_exchange(
    routing_key: str, body: dict, exchange: str, virtual_host: str
) -> bool:
    """
    Publish a message to an exchange on a RabbitMQ broker.

    :param routing_key: str - The routing key for the message.
    :param body: dict - The message body as a dictionary.
    :param exchange: str - The exchange to publish the message to.
    :param virtual_host: str - The virtual host on the RabbitMQ server to use.

    :return: bool - True if the message was successfully published, False otherwise.
    """
    credentials = pika.PlainCredentials(*AUTH)
    ssl_options = None

    if Configurations.RABBITMQ_SSL_ACTIVE:
        context = ssl.create_default_context()
        ssl_options = pika.SSLOptions(context)

    conn_params = pika.ConnectionParameters(
        host=Configurations.RABBITMQ_HOST,
        port=Configurations.RABBITMQ_SERVER_PORT_SSL
        if Configurations.RABBITMQ_SSL_ACTIVE
        else Configurations.RABBITMQ_SERVER_PORT,
        virtual_host=virtual_host,
        credentials=credentials,
        ssl_options=ssl_options,
    )

    try:
        with pika.BlockingConnection(conn_params) as connection:
            channel = connection.channel()

            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(body),
                properties=pika.BasicProperties(
                    delivery_mode=2
                ),  # make message persistent
            )

    except Exception as error:
        raise error

    logger.info("Successfully published to queue '%s'", routing_key)
    return True
