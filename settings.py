"""Module for Configurations"""
import os

MODE = os.environ.get("MODE")

if MODE and MODE.lower() == "production":

    class Production:
        """Production Configurations"""

        SSL_PORT = os.environ["SSL_PORT"]
        SSL_CERTIFICATE = os.environ["SSL_CERTIFICATE"]
        SSL_KEY = os.environ["SSL_KEY"]
        SSL_PEM = os.environ["SSL_PEM"]

        COOKIE_SECURE = True

    BaseConfig = Production

else:

    class Development:
        """Development Configurations"""

        SSL_PORT = os.environ.get("SSL_PORT")
        SSL_CERTIFICATE = os.environ.get("SSL_CERTIFICATE") or ""
        SSL_KEY = os.environ.get("SSL_KEY") or ""
        SSL_PEM = os.environ.get("SSL_PEM") or ""

        COOKIE_SECURE = False

    BaseConfig = Development


class Configurations(BaseConfig):
    """Base Configurations"""

    MYSQL_HOST = os.environ.get("MYSQL_HOST")
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE")

    ENCRYPTION_KEY = os.environ["ENCRYPTION_KEY"]
    HASH_SALT = os.environ["HASH_SALT"]

    HOST = os.environ.get("HOST")
    PORT = os.environ.get("PORT")
    ORIGINS = os.environ.get("ORIGINS")

    COOKIE_NAME = "deku"
    COOKIE_MAXAGE = 15 * 60000  # 15 mins in ms
    COOKIE_HTTPONLY = True
    COOKIE_SAMESITE = "lax"

    RABBITMQ_USER = os.environ.get("RABBITMQ_USER") or "guest"
    RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD") or "guest"
    RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST") or os.environ.get("HOST")
    RABBITMQ_MANAGEMENT_PORT = os.environ.get("RABBITMQ_MANAGEMENT_PORT") or "15672"
    RABBITMQ_SERVER_PORT = os.environ.get("RABBITMQ_SERVER_PORT") or "5672"

    RABBITMQ_SSL_ACTIVE = os.environ.get("RABBITMQ_SSL_ACTIVE").lower() in ["true"]
    RABBITMQ_MANAGEMENT_PORT_SSL = (
        os.environ.get("RABBITMQ_MANAGEMENT_PORT_SSL") or "15671"
    )
    RABBITMQ_SERVER_PORT_SSL = os.environ.get("RABBITMQ_SERVER_PORT_SSL") or "5671"
