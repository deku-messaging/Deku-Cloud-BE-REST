"""Peewee Handler for log model"""

import logging
from uuid import uuid4

from src.orm.peewee.models.log import Log

logger = logging.getLogger(__name__)


class LogHandler:
    """
    A class for handling CRUD operations on the Log model.
    """

    def create_log(
        self, service_id: str, project_reference: str, to_: str, status: str, **kwargs
    ) -> Log:
        """
        Create a new log record.

        :param service_id: str: The unique identifier for the service.
        :param project_reference: str: A unique reference for the project.
        :param to_: str: The recipient of the message.
        :param status: str: The current status of the log.
        :param kwargs: dict: Additional fields to include in the log record.

        :return: Log: The newly created log record.
        """
        log_fields = {
            "sid": kwargs.get("sid", uuid4().hex.upper()),
            "service_id": service_id,
            "project_reference": project_reference,
            "to": to_,
            "status": status,
            "service_name": kwargs.get("service_name"),
            "direction": kwargs.get("direction"),
            "from_": kwargs.get("from_"),
            "channel": kwargs.get("channel"),
            "reason": kwargs.get("reason"),
            "user_id": kwargs.get("user_id"),
        }

        try:
            log = Log.create(**log_fields)
            logger.info("Successfully created log")
            return log
        except Exception as error:
            logger.error("Error creating log")
            raise error
