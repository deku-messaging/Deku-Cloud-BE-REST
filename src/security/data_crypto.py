"""Module for data cryptography."""

import logging

from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA512
from Crypto.Util.Padding import pad, unpad
from Crypto import Random

from werkzeug.exceptions import Unauthorized

from settings import Configurations

SHARED_KEY = Configurations.SHARED_KEY
HASHING_SALT = Configurations.HASHING_SALT

logger = logging.getLogger(__name__)


class DataCrypto:
    """DataCryptography"""

    def __init__(self):
        self.shared_key = SHARED_KEY.encode("utf-8")
        self.hashing_salt = HASHING_SALT.encode("utf-8")
        self.iv_ = Random.new().read(AES.block_size).hex()[:16].encode("utf-8")

    def encrypt(self, data: str, iv_: str = None) -> object:
        """Encrypt data with AES-CBC cipher mode.

        Keyword arguments:
        data -- content to be encrypted

        return: object
        """

        class Result:
            """return"""

            ciphertext = None
            iv = None

        if not data:
            logger.info("[x] Nothing to encrypt")
            return Result

        logger.debug("[*] Starting encryption ...")

        try:
            data_bytes = data.encode("utf-8")
            iv_bytes = self.iv_ if not iv_ else iv_.encode("utf-8")
            cipher = AES.new(self.shared_key, AES.MODE_CBC, iv_bytes)
            ct_bytes = cipher.encrypt(pad(data_bytes, 16))

        except Exception as error:
            logger.error("[!] Error encrypting data. See logs below")
            raise error

        else:
            Result.ciphertext = ct_bytes.hex()
            Result.iv = cipher.iv.decode("utf-8")

            logger.info("[x] Successfully encrypted data")
            return Result

    def decrypt(self, data: str, iv_: str) -> str:
        """Decrypt data encrypted with AES-CBC cipher mode.

        Keyword arguments:
        data -- content ot be decrypted
        iv -- initialization vector of ecrypted data

        return: str
        """

        if not data:
            logger.info("[x] Nothing to decrypt")
            return None

        logger.debug("[*] Starting decryption ...")

        try:
            iv_str = iv_.encode("utf-8")
            ct_ = bytes.fromhex(data)
            cipher = AES.new(self.shared_key, AES.MODE_CBC, iv_str)
            pt_ = unpad(cipher.decrypt(ct_), 16)

        except (ValueError, KeyError) as error:
            logger.error("[!] Error decrypting data. See logs below")
            logger.exception(error)
            raise Unauthorized from error

        else:
            logger.info("[x] Successfully decrypted data")
            return pt_.decode("utf-8")

    def hash(self, data: str, hashing_salt: str = None) -> str:
        """Hash data with HMAC-512 hash algorithm

        Keyword arguments:
        data -- content to be hashed

        returns: str
        """

        logger.debug("[*] Starting hash ...")

        try:
            data_bytes = data.encode("utf-8")
            hashing_salt_bytes = (
                self.hashing_salt if not hashing_salt else hashing_salt.encode("utf-8")
            )
            mac = HMAC.new(hashing_salt_bytes, data_bytes, SHA512)

        except Exception as error:
            logger.error("[!] Error hashing data. See logs below")
            raise error

        else:
            logger.info("[x] Successfully hashed data")
            return mac.hexdigest()
