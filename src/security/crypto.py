"""Cryptography Module"""

import logging
import secrets
import hashlib
from base64 import b64encode, b64decode

import bcrypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from settings import Configurations

logger = logging.getLogger(__name__)


class DataSecurity:
    """
    A class for encrypting, decrypting, and hashing user data.

    Attributes:
        encryption_key (str): A 32-byte AES encryption key for encrypting and decrypting data.
        hash_key (str): A key for the SHA512 algorithm for hashing data.
        hash_salt (bytes): A randomly generated 16-byte salt value for the SHA512 algorithm.
    """

    def __init__(self, encryption_key=None, hash_key=None):
        """
        Initializes a new DataSecurity object with the provided encryption key and hash key.

        Args:
            encryption_key (str): A 32-byte AES encryption key for encrypting and decrypting data.
            hash_key (str): A key for the SHA512 algorithm for hashing data.
        """

        self.encryption_key = (encryption_key or Configurations.ENCRYPTION_KEY).encode(
            "utf-8"
        )
        self.hash_key = (hash_key or Configurations.HASH_SALT).encode("utf-8")

        logger.info("DataSecurity object initialized successfully")

    def encrypt_data(self, plaintext: str) -> str:
        """
        Encrypts the provided plaintext using the AES encryption algorithm in CBC mode
        with a randomly generated 16-byte initialization vector (IV).

        Args:
            plaintext (str): The plaintext data to encrypt.

        Returns:
            str: The encrypted data in string format, including the IV as a prefix.
        """

        try:
            if not plaintext:
                logger.error("Empty plaintext provided for encryption")
                return ""

            iv_value = secrets.token_bytes(16)
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv=iv_value)
            plaintext_bytes = plaintext.encode("utf-8")
            padded_plaintext = pad(plaintext_bytes, AES.block_size)
            encrypted_data = cipher.encrypt(padded_plaintext)
            encrypted_data_with_iv = iv_value + encrypted_data

            logger.info("Plaintext has been encrypted successfully")

            return b64encode(encrypted_data_with_iv)

        except Exception as error:  # pylint: disable=broad-exception-caught
            logger.error("Error occurred while encrypting data")
            raise error

    def decrypt_data(self, ciphertext: str) -> str:
        """
        Decrypts the provided ciphertext using the AES encryption algorithm in CBC mode
        with the initialization vector (IV) extracted from the beginning of the ciphertext.

        Args:
            ciphertext (str): The encrypted data to decrypt, including the IV as a prefix.

        Returns:
            str: The decrypted data in string format.
        """

        try:
            if not ciphertext:
                logger.error("Empty ciphertext provided for decryption")
                return None

            ciphertext = b64decode(ciphertext)

            if len(ciphertext) < 16:
                logger.error("Invalid ciphertext provided for decryption")
                raise ValueError

            iv_value = ciphertext[:16]
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv=iv_value)
            ciphertext_bytes = ciphertext[16:]
            decrypted_data = cipher.decrypt(ciphertext_bytes)
            unpadded_data = unpad(decrypted_data, AES.block_size)

            logger.info("Ciphertext has been decrypted successfully")

            return unpadded_data.decode()

        except Exception as error:  # pylint: disable=broad-exception-caught
            logger.error("Error occurred while decrypting data")
            raise error

    def hash_data(self, data):
        """
        Hashes the provided data using the SHA512 hashing algorithm with a randomly generated salt.

        Args:
            data (str): The data to hash.

            Returns:
            str: The hashed data in string format.
        """

        try:
            if not data:
                logger.error("Empty data provided for hashing")
                return None

            hash_salt = secrets.token_bytes(16)

            salted_data = data.encode("utf-8") + hash_salt + self.hash_key
            hashed_data = hashlib.sha512(salted_data).hexdigest()

            logger.info("Data has been hashed successfully")

            return hashed_data

        except Exception as error:  # pylint: disable=broad-exception-caught
            logger.error("Error occurred while hashing data")
            raise error

    def hash_password(self, password: str) -> str:
        """
        Hashes the provided password using bcrypt.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password in string format.
        """
        try:
            hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
            return hashed.decode("utf-8")
        except Exception as error:
            logger.error("Error occurred while hashing password")
            raise error

    def check_password(self, password: str, hashed_password: str) -> bool:
        """
        Checks if the provided password matches the hashed password using bcrypt.

        Args:
            password (str): The password to check.
            hashed_password (str): The hashed password to compare to.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"), hashed_password.encode("utf-8")
            )
        except Exception as error:
            logger.error("Error occurred while checking password")
            raise error
