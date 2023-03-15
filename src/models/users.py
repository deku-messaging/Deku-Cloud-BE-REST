"""Users Handler"""

import logging
from uuid import uuid1

from Crypto.Hash import MD5
from werkzeug.exceptions import Conflict, Unauthorized

from src.schemas.users import Users
from src.security.data_crypto import DataCrypto

from src.models.rabbitmq import RabbitMQModel

logger = logging.getLogger(__name__)


class UserModel:
    """Handler definition"""

    def __init__(self):
        self.users = Users
        self.data_crypto = DataCrypto
        self.rabbitmq = RabbitMQModel

    def create(
        self,
        email: str,
        password: str,
        name: str,
        phone_number: str = None,
    ) -> object:
        """Create an account.

        Keyword arguments:
        email -- user's email (unique)
        password -- user's password
        name -- user's name
        phone_number -- user's primary phone number

        return: object
        """

        data_security = self.data_crypto()
        rabbitmq = self.rabbitmq()

        account_sid = "AC" + MD5.new(email.encode("utf-8")).hexdigest()
        auth_token = MD5.new(str(uuid1()).encode("utf-8")).hexdigest()

        try:
            logger.debug("[*] Finding user '%s' ...", email)

            user = self.users.get(
                self.users.email_hash == data_security.hash(data=email)
            )

        except self.users.DoesNotExist:
            try:
                logger.debug("[*] Creating user '%s' ...", email)

                user = self.users.create(
                    email=data_security.encrypt(data=email).ciphertext,
                    password=data_security.hash(data=password),
                    name=data_security.encrypt(data=name).ciphertext,
                    email_hash=data_security.hash(data=email),
                    phone_number=data_security.encrypt(data=phone_number).ciphertext,
                    account_sid=account_sid,
                    auth_token=auth_token,
                    iv=data_security.iv_,
                )

                rabbitmq.add_user(username=user.account_sid, password=user.auth_token)

                logger.info("[x] Successfully created user")

                return user

            except Exception as error:
                logger.error("[!] Error creating user. See logs below")
                raise error

        else:
            logger.error("[!] User '%s' exists", user.email)
            raise Conflict()

    def verify(self, email: str, password: str) -> object:
        """Verify an account's credentials.

        Keyword arguments:
        email -- user's email (unique)
        password -- user's password

        return: object
        """

        data_security = self.data_crypto()

        try:
            logger.debug("[*] Finding user '%s' ...", email)

            user = self.users.get(
                self.users.email_hash == data_security.hash(data=email),
                self.users.password == data_security.hash(data=password),
            )

        except self.users.DoesNotExist as error:
            logger.error("[!] User not Found")
            raise Unauthorized() from error

        else:
            logger.info("[x] User Found")
            return user

    def authenticate(self, account_sid: str, auth_token: str) -> bool:
        """Authenticate an account's tokens.

        Keyword arguments:
        account_sid -- user's account_sid
        auth_token -- user's auth_token

        return: bool
        """

        try:
            logger.debug("[*] Authenticating tokens ...")

            self.users.get(
                self.users.account_sid == account_sid,
                self.users.auth_token == auth_token,
            )

        except self.users.DoesNotExist:
            logger.error("[!] Invalid tokens")
            return False

        else:
            logger.info("[x] Valid tokens")
            return True

    def find_one(self, account_sid: str) -> object:
        """Find a single user account.

        Keyword arguments:
        account_sid -- user's account_sid

        return: object
        """

        try:
            logger.debug("[*] Finding user ...")

            user = self.users.get(self.users.account_sid == account_sid)

        except self.users.DoesNotExist:
            raise Unauthorized()

        else:
            logger.info("[x] User Found")
            return user
