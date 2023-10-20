"""User API Endpoints"""

import logging
import json
from datetime import timedelta
import csv
import threading

from flask import request, Blueprint, Response, jsonify, after_this_request
from playhouse.shortcuts import model_to_dict

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
from src.orm.peewee.handlers.log import LogHandler
from src.orm.peewee.handlers.user import UserHandler
from src.controllers import user, project, service


logger = logging.getLogger(__name__)

v1 = Blueprint("v1", __name__)

COOKIE_NAME = Configurations.COOKIE_NAME


@v1.after_request
def after_request(response):
    """After request decorator"""
    try:
        database.close()

        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=63072000; includeSubdomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers[
            "Content-Security-Policy"
        ] = "script-src 'self'; object-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cache-Control"] = "no-cache"
        response.headers[
            "Permissions-Policy"
        ] = "accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), camera=(), clipboard-read=(), clipboard-write=(), cross-origin-isolated=(), display-capture=(), document-domain=(), encrypted-media=(), execution-while-not-rendered=(), execution-while-out-of-viewport=(), fullscreen=(), gamepad=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), midi=(), navigation-override=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), screen-wake-lock=(), speaker=(), speaker-selection=(), sync-xhr=(), usb=(), web-share=(), xr-spatial-tracking=()"

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


@v1.route("/", methods=["GET", "PUT", "DELETE"])
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

        if method == "delete":
            json_data = request.json

            if not user.delete_user(user_id=session.unique_identifier, **json_data):
                raise Unauthorized()

            res = Response()

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
def project_endpoint():
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
            description = request.json.get("description")
            reference = request.json.get("reference")

            if reference:
                if len(reference) < 2:
                    message = "Reference must be at least 2 characters long"
                    logger.error(message)
                    raise BadRequest(message)

                allowed_chars = set(
                    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
                )

                disallowed_chars = set(reference).difference(allowed_chars)

                if disallowed_chars:
                    message = f"Reference can only contain letters, numbers, underscores, and hyphens, not {disallowed_chars}"
                    logger.error(message)
                    raise BadRequest(message)

            created_project = project.create_project(
                friendly_name=friendly_name,
                description=description,
                user_id=session.unique_identifier,
                reference=reference,
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
def single_project_endpoint(project_id):
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
            current_project = project.get_project_by_id(project_id=project_id)
            if not current_project:
                raise NotFound(f"Project with ID '{project_id}' not found")

        if method.lower() == "put":
            friendly_name = request.json.get("friendly_name")
            description = request.json.get("description")

            current_project = project.update_project(
                project_id=project_id,
                friendly_name=friendly_name,
                description=description,
            )
            if not current_project:
                raise NotFound(f"Project with ID '{project_id}' not found")

        if method.lower() == "delete":
            if not project.delete_project(project_id=project_id):
                raise NotFound(f"Project with ID '{project_id}' not found")

            current_project = ""

        res = jsonify(current_project)

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


@v1.route("/logs", methods=["GET"])
def log_endpoint():
    """Manage Logs"""

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
        log_handler = LogHandler()

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

            [total, logs_list] = log_handler.get_logs_by_field(
                user_id=session.unique_identifier,
                **input_data,
            )

            res = jsonify([model_to_dict(log, recurse=False) for log in logs_list])

            if request.args.get("range"):
                res.headers[
                    "Content-Range"
                ] = f"rows {input_data['data_range'][0]}-{input_data['data_range'][1]}/{total}"
                res.headers["Access-Control-Expose-Headers"] = "Content-Range"

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


@v1.route("/logs/<string:log_id>", methods=["PUT"])
def single_log_endpoint(log_id):
    """Single Log Endpoint"""

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
        log_handler = LogHandler()

        session = session_handler.get_session_by_field(
            sid=sid, user_agent=user_agent, status=session_status
        )

        if not session:
            raise Unauthorized()

        if method == "put":
            if not request.json.get("status"):
                logger.error("No status provided")
                raise BadRequest()

            status = request.json.get("status")

            if status.lower() not in ["delivered", "failed"]:
                logger.error("Invalid log status: %s", status)
                raise BadRequest(f"Invalid log status: {status}")

            if not log_handler.update_log(log_id=log_id, status=status):
                raise NotFound(f"Log with ID '{log_id}' not found")

            current_log = ""

        res = jsonify(current_log)

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


@v1.route("/projects/<string:reference>/services/<string:service_id>", methods=["POST"])
def publish_endpoint(reference: str, service_id: str):
    """Publish Endpoint"""

    results = {"message": "", "errors": [], "warnings": [], "response": []}

    try:
        if not request.authorization:
            logger.error("No Authorization header")
            raise Unauthorized()

        if not request.authorization.get("username"):
            logger.error("No username")
            raise BadRequest()

        if not request.authorization.get("password"):
            logger.error("No password")
            raise BadRequest()

        if not service_id.lower() in ["sms", "notification"]:
            logger.error("Invalid service: %s", service_id)
            raise BadRequest()

        username = request.authorization.get("username")
        password = request.authorization.get("password")

        # Handle JSON payload
        payload = []
        required_keys = {"body", "to"}

        if request.is_json:
            json_data = request.get_json()

            if isinstance(json_data, list):
                for item in json_data:
                    result = {
                        "sid": item.get("sid"),
                        "message": "",
                        "errors": [],
                        "warnings": [],
                    }

                    missing_keys = required_keys.difference(item.keys())

                    if missing_keys:
                        missing_key = missing_keys.pop()
                        result["errors"].append(f"Missing required key '{missing_key}'")

                    else:
                        payload.append(
                            {
                                "body": item["body"],
                                "to": item["to"],
                                "sid": item.get("sid"),
                            }
                        )
                        result["message"] = "queued"

                    results["response"].append(result)
            elif isinstance(json_data, dict):
                result = {
                    "sid": json_data.get("sid"),
                    "message": "",
                    "errors": [],
                    "warnings": [],
                }

                missing_keys = required_keys.difference(json_data.keys())

                if missing_keys:
                    missing_key = missing_keys.pop()
                    result["errors"].append(f"Missing required key '{missing_key}'")

                else:
                    payload.append(
                        {
                            "body": json_data["body"],
                            "to": json_data["to"],
                            "sid": json_data.get("sid"),
                        }
                    )
                    result["message"] = "queued"

                results["response"].append(result)
            else:
                results["errors"].append(f"Invalid JSON payload format: {json_data}")

        # Handle uploaded CSV file
        if "file" in request.files:
            file = request.files["file"]

            if file and file.filename.endswith(".csv"):
                csv_data = csv.DictReader(file.read().decode("utf-8").splitlines())

                for idx, row in enumerate(csv_data, start=1):
                    result = {
                        "sid": row.get("sid"),
                        "message": "",
                        "errors": [],
                        "warnings": [],
                    }

                    missing_keys = required_keys.difference(row.keys())

                    if missing_keys:
                        missing_key = missing_keys.pop()
                        result["errors"].append(
                            f"Missing required key '{missing_key}' at line {idx+1}"
                        )

                    else:
                        payload.append(
                            {
                                "body": row["body"],
                                "to": row["to"],
                                "sid": row.get("sid"),
                            }
                        )
                        result["message"] = "queued"

                    results["response"].append(result)
            else:
                results["errors"].append("Invalid file format or no file uploaded")

        if not payload:
            results["warnings"].append("No valid payload found. No message was sent")

            return jsonify(results), 200

        user_handler = UserHandler()

        [user_total, users_list] = user_handler.get_users_by_field(
            account_sid=username, auth_token=password
        )

        if user_total < 1 and len(users_list) < 1:
            logger.error("User not found.")
            raise Unauthorized()

        current_user = user.get_user_by_id(user_id=users_list[0].id)

        [project_total, projects_list] = project.get_projects_by_field(
            reference=reference, user_id=current_user.get("id")
        )

        if project_total < 1 and len(projects_list) < 1:
            err_message = f"Project with reference {reference} not found"
            logger.error(err_message)
            raise NotFound(err_message)

        def send_messages():
            for item in payload:
                service.publish_to_service(
                    service_id=service_id,
                    content=item["body"],
                    project_reference=reference,
                    phone_number=item["to"].replace(" ", ""),
                    user=current_user,
                    sid=item["sid"],
                )

        @after_this_request
        def send_messages_after_request(response):
            # Start a new thread to send messages
            thread = threading.Thread(target=send_messages)
            thread.start()
            return response

        if any(result["errors"] for result in results["response"]):
            results["warnings"].append("Some messages failed to process due to errors.")
            return jsonify(results), 200

        results["message"] = "Processing all messages ..."
        return jsonify(results), 200

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
