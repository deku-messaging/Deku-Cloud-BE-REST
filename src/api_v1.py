"""User API Endpoints"""

import logging
import json
from datetime import timedelta

from flask import request, Blueprint, Response, jsonify

from werkzeug.exceptions import (
    InternalServerError,
    BadRequest,
    Conflict,
    Unauthorized,
    NotFound,
)

from settings import Configurations
from src.orm.peewee.connector import database

from src.security.password_policy import check_password_policy

from src.orm.peewee.handlers.session import SessionHandler
from src.controllers import user, project


logger = logging.getLogger(__name__)

v1 = Blueprint("v1", __name__)

COOKIE_NAME = Configurations.COOKIE_NAME


@v1.after_request
def after_request(response):
    """After request decorator"""
    try:
        database.close()
        return response

    except Exception as error:
        logger.exception(error)
        return "Internal Server Error", 500


@v1.route("/signup", methods=["POST"])
def signup():
    """Signup Endpoint"""

    try:
        if not request.headers.get("User-Agent"):
            logger.error("No user agent")
            raise BadRequest()

        if not request.json.get("email"):
            logger.error("No email provided")
            raise BadRequest()

        if not request.json.get("password"):
            logger.error("No password provided")
            raise BadRequest()

        email = request.json.get("email")
        password = request.json.get("password")
        first_name = request.json.get("first_name")
        last_name = request.json.get("last_name")
        phone_number = request.json.get("phone_number")

        check_password_policy(password=password)

        if not user.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        ):
            raise Conflict()

        return Response(), 200

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


@v1.route("/login", methods=["POST"])
def login():
    """Login Endpoint"""

    try:
        if not request.headers.get("User-Agent"):
            logger.error("No user agent")
            raise BadRequest()

        if not request.json.get("email"):
            logger.error("No email provided")
            raise BadRequest()

        if not request.json.get("password"):
            logger.error("No password provided")
            raise BadRequest()

        user_agent = request.headers.get("User-Agent")
        email = request.json.get("email")
        password = request.json.get("password")
        session_status = "active"

        session_handler = SessionHandler()

        current_user = user.verify_user(email=email, password=password)

        if not current_user:
            raise Unauthorized()

        new_session = session_handler.create_session(
            unique_identifier=current_user["id"],
            user_agent=user_agent,
            status=session_status,
        )

        session_data = json.loads(new_session.data)

        res = jsonify(
            {
                "account_sid": str(current_user["account_sid"]),
                "auth_token": str(current_user["auth_token"]),
            }
        )

        res.set_cookie(
            COOKIE_NAME,
            str(new_session.sid),
            max_age=timedelta(milliseconds=session_data["max_age"]),
            secure=session_data["secure"],
            httponly=session_data["httponly"],
            samesite=session_data["samesite"],
        )

        return res, 200

    except BadRequest as err:
        return str(err), 400

    except Conflict as err:
        return str(err), 409

    except Unauthorized as err:
        return str(err), 401

    except InternalServerError as err:
        logger.exception(err)
        return "Internal Server Error", 500

    except Exception as error:
        logger.exception(error)
        return "Internal Server Error", 500


@v1.route("/", methods=["GET", "PUT"])
def index():
    """Manage Authenticated user's account"""

    method = request.method.lower()

    try:
        if not request.headers.get("User-Agent"):
            logger.error("No user agent")
            raise BadRequest()

        if not request.cookies.get(COOKIE_NAME):
            logger.error("No cookie")
            raise Unauthorized()

        user_agent = request.headers.get("User-Agent")
        sid = request.cookies.get(COOKIE_NAME)
        session_status = "active"

        session_handler = SessionHandler()

        session = session_handler.get_session_by_field(
            sid=sid, user_agent=user_agent, status=session_status
        )

        if not session:
            raise Unauthorized()

        if method == "get":
            current_user = user.get_user_by_id(user_id=session.unique_identifier)

            if not current_user:
                raise Unauthorized()

            res = jsonify(current_user)

        if method == "put":
            json_data = request.json

            updated_user = user.update_user(
                user_id=session.unique_identifier, **json_data
            )

            res = jsonify(updated_user)

        session = session_handler.update_session(session_id=sid)

        session_data = json.loads(session.data)

        res.set_cookie(
            COOKIE_NAME,
            str(session.sid),
            max_age=timedelta(milliseconds=session_data["max_age"]),
            secure=session_data["secure"],
            httponly=session_data["httponly"],
            samesite=session_data["samesite"],
        )

        return res, 200

    except BadRequest as err:
        return str(err), 400

    except Conflict as err:
        return str(err), 409

    except Unauthorized as err:
        return str(err), 401

    except InternalServerError as err:
        logger.exception(err)
        return "Internal Server Error", 500

    except Exception as error:
        logger.exception(error)
        return "Internal Server Error", 500


@v1.route("/projects", methods=["POST", "GET"])
def project_handler():
    """Manage Projects"""

    method = request.method.lower()

    try:
        if not request.headers.get("User-Agent"):
            logger.error("No user agent")
            raise BadRequest()

        if not request.cookies.get(COOKIE_NAME):
            logger.error("No cookie")
            raise Unauthorized()

        user_agent = request.headers.get("User-Agent")
        sid = request.cookies.get(COOKIE_NAME)
        session_status = "active"

        session_handler = SessionHandler()

        session = session_handler.get_session_by_field(
            sid=sid, user_agent=user_agent, status=session_status
        )

        if not session:
            raise Unauthorized()

        if method == "get":
            input_data = {}

            if request.args.get("filter"):
                input_data = {**json.loads(request.args.get("filter"))}

            if request.args.get("sort"):
                input_data["sort"] = json.loads(request.args.get("sort"))

            if request.args.get("range"):
                input_data["data_range"] = json.loads(request.args.get("range"))

            [total, projects_list] = project.get_projects_by_field(
                user_id=session.unique_identifier,
                **input_data,
            )

            res = jsonify(projects_list)

            if request.args.get("range"):
                res.headers[
                    "Content-Range"
                ] = f"rows {input_data['data_range'][0]}-{input_data['data_range'][1]}/{total}"
                res.headers["Access-Control-Expose-Headers"] = "Content-Range"

        if method == "post":
            if not request.json.get("friendly_name"):
                logger.error("No friendly name provided")
                raise BadRequest()

            friendly_name = request.json.get("friendly_name")

            created_project = project.create_project(
                friendly_name=friendly_name, user_id=session.unique_identifier
            )

            if not created_project:
                raise Conflict()

            res = jsonify(created_project)

        session = session_handler.update_session(session_id=sid)

        session_data = json.loads(session.data)

        res.set_cookie(
            COOKIE_NAME,
            str(session.sid),
            max_age=timedelta(milliseconds=session_data["max_age"]),
            secure=session_data["secure"],
            httponly=session_data["httponly"],
            samesite=session_data["samesite"],
        )

        return res, 200

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


@v1.route("/projects/<string:project_id>", methods=["GET", "PUT", "DELETE"])
def single_project(project_id):
    """Single Project Endpoint"""

    method = request.method.lower()

    try:
        if not request.headers.get("User-Agent"):
            logger.error("No user agent")
            raise BadRequest()

        if not request.cookies.get(COOKIE_NAME):
            logger.error("No cookie")
            raise Unauthorized()

        user_agent = request.headers.get("User-Agent")
        sid = request.cookies.get(COOKIE_NAME)
        session_status = "active"

        session_handler = SessionHandler()

        session = session_handler.get_session_by_field(
            sid=sid, user_agent=user_agent, status=session_status
        )

        if not session:
            raise Unauthorized()

        if method.lower() == "get":
            project_current = project.get_project_by_id(project_id=project_id)
            if not project_current:
                raise NotFound(f"Project with ID '{project_id}' not found")

        res = jsonify(project_current)

        session = session_handler.update_session(session_id=sid)

        session_data = json.loads(session.data)

        res.set_cookie(
            COOKIE_NAME,
            str(session.sid),
            max_age=timedelta(milliseconds=session_data["max_age"]),
            secure=session_data["secure"],
            httponly=session_data["httponly"],
            samesite=session_data["samesite"],
        )

        return res, 200

    except BadRequest as err:
        return str(err), 400

    except Unauthorized as err:
        return str(err), 401

    except NotFound as err:
        return str(err), 404

    except InternalServerError as err:
        logger.exception(err)
        return "Internal Server Error", 500

    except Exception as error:
        logger.exception(error)
        return "Internal Server Error", 500


# @v1.route("/projects/<string:pid>/services/<string:service>", methods=["POST"])
# def publish(pid: str, service: str):
#     """Publish Endpoint"""

#     try:
#         if not request.authorization:
#             logger.error("No Authorization header")
#             raise Unauthorized()

#         if not request.authorization.get("username"):
#             logger.error("No username")
#             raise BadRequest()

#         if not request.authorization.get("password"):
#             logger.error("No password")
#             raise BadRequest()

#         if not service.lower() in ["sms", "notification"]:
#             logger.error("Invalid service: %s", service)
#             raise BadRequest()

#         if not request.json.get("body"):
#             logger.error("No body")
#             raise BadRequest()

#         if not request.json.get("to"):
#             logger.error("No contact to send to")
#             raise BadRequest()

#         username = request.authorization.get("username")
#         password = request.authorization.get("password")
#         body = request.json.get("body")
#         to_ = request.json.get("to")
#         body = request.json.get("body")

#         user = UserModel()
#         project = ProjectModel()
#         service_ = ServerModel(service=service)

#         if not user.authenticate(account_sid=username, auth_token=password):
#             raise Unauthorized()

#         user_ = user.find_one(account_sid=username)
#         project.find_one(pid=pid, user_id=user_.id)

#         message = service_.publish(
#             content=body,
#             identifier=to_,
#             user=user_,
#             pid=pid,
#         )

#         res = jsonify(message)

#         return res, 200

#     except BadRequest as err:
#         return str(err), 400

#     except Unauthorized as err:
#         return str(err), 401

#     except NotFound as err:
#         return str(err), 404

#     except InternalServerError as err:
#         logger.exception(err)
#         return "Internal Server Error", 500

#     except Exception as error:
#         logger.exception(error)
#         return "Internal Server Error", 500
