"""Password Policy Module"""

import logging

from werkzeug.exceptions import BadRequest

logger = logging.getLogger(__name__)


def password_check(password: str) -> bool:
    """Check if password follows policy

    Keyword arguments:
    password -- Password provided

    return: str
    """

    special_chars = ["!", "@", "#", "$", "%", "^", "&", "*"]

    if len(password) < 6:
        msg = "Password length should be at least 6"
        logger.error("[!] %s", msg)
        raise BadRequest(msg)

    if len(password) > 20:
        msg = "Password length should be not be greater than 20"
        logger.error("[!] %s", msg)
        raise BadRequest(msg)

    if not any(char.isdigit() for char in password):
        msg = "Password should have at least one numeral"
        logger.error("[!] %s", msg)
        raise BadRequest(msg)

    if not any(char.isupper() for char in password):
        msg = "Password should have at least one uppercase letter"
        logger.error("[!] %s", msg)
        raise BadRequest(msg)

    if not any(char.islower() for char in password):
        msg = "Password should have at least one lowercase letter"
        logger.error("[!] %s", msg)
        raise BadRequest(msg)

    if not any(char in special_chars for char in password):
        msg = f"Password should have at least one of the symbols ({''.join(special_chars)})"
        logger.error("[!] %s", msg)
        raise BadRequest(msg)

    logger.info("[x] Password Conforms to Password Policy.")
    return True
