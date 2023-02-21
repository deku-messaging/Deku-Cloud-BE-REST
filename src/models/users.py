"""Users Handler"""

import logging
from datetime import datetime
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

    def find(self, id_: str) -> object:
        """Find an account.

        Keyword arguments:
        id_ -- user's id (unique)

        return: object
        """

        class Result:
            """return"""

            email = None
            name = None
            phone_number = None
            address = None

        data_security = self.data_crypto()

        try:
            logger.debug("[*] Finding user_id '%s' ...", id_)

            user = self.users.get(
                self.users.id == id_, self.users.account_status == "approved"
            )

        except self.users.DoesNotExist as error:
            logger.error("[!] User not Found")
            raise Unauthorized() from error

        else:
            Result.email = data_security.decrypt(data=user.email, iv_=user.iv)
            Result.name = data_security.decrypt(data=user.name, iv_=user.iv)
            Result.phone_number = data_security.decrypt(
                data=user.phone_number, iv_=user.iv
            )
            Result.address = data_security.decrypt(data=user.address, iv_=user.iv)

            logger.info("[x] User Found")

            return Result

    def update(self, id_: str) -> object:
        """Update a user's account.

        Keyword arguments:
        id_ -- user's id (unique)

        return: object
        """

        try:
            logger.debug("[*] Updating user '%s' ...", id_)

            user = self.users.update(last_seen=datetime.now()).where(
                self.users.id == id_
            )

            user.execute()

        except Exception as error:
            logger.error("[!] Error updating user. See logs below")
            raise error
