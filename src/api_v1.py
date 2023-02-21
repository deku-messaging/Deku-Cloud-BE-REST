"""User API Endpoints"""

import logging

from flask import request, Blueprint

from werkzeug.exceptions import InternalServerError, BadRequest, Conflict, Unauthorized

from src.schemas.db_connector import connection

from src.models.users import UserModel

logger = logging.getLogger(__name__)

v1 = Blueprint("v1", __name__)


@v1.after_request
def after_request(response):
    """After request decorator"""
    try:
        connection.close()
        return response

    except Exception as error:
        logger.exception(error)
        return "Internal Server Error", 500


@v1.route("/signup", methods=["POST"])
def signup():
    """Signup Endpoint"""

    try:
        if not request.headers.get("User-Agent"):
            logger.error("[!] No user agent")
            raise BadRequest()

        if not request.json.get("email"):
            logger.error("[!] No email provided")
            raise BadRequest()

        if not request.json.get("password"):
            logger.error("[!] No password provided")
            raise BadRequest()

        email = request.json.get("email")
        password = request.json.get("password")
        name = request.json.get("name")
        phone_number = request.json.get("phone_number")

        user = UserModel()

        user.create(
            email=email,
            password=password,
            name=name,
            phone_number=phone_number,
        )

        return "", 200

    except BadRequest as err:
        return str(err), 400

    except Unauthorized as err:
        return str(err), 401

    except Conflict as err:
        return str(err), 409

    except InternalServerError as err:
        logger.exception(err)
        return "Internal Server Error", 500

    except Exception as error:
        logger.exception(error)
        return "Internal Server Error", 500
