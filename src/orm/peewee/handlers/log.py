"""Peewee Handler for log model"""

import logging
from datetime import datetime
from typing import Optional
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

    def get_log_by_id(self, log_id: int) -> Optional[Log]:
        """Retrieve a log by its ID.

        :param log_id: int - The ID of the log to retrieve.

        :return: Optional[Log] - The retrieved log, or None if no log with that ID exists.
        """
        try:
            log = Log.get(id=log_id)
            return log

        except Log.DoesNotExist:
            logger.error("Log with ID %s does not exist.", log_id)
            return None

    def get_logs_by_field(
        self, data_range: list = None, sort: list = None, **kwargs
    ) -> list:
        """Retrieve all logs with the given field(s).

        :param data_range: list - A list of two int values representing the offset and limit of the data to retrieve. Default is None, which retrieves all logs.
        :param sort: list - A list of field and order to sort the logs by. Default is None, which returns the logs in the order they were retrieved.
        :param kwargs: dict - fields for logs to retrieve. Default is None, which retrieves all logs.

        :return: list - A list of the total number of records retrieved and the retrieved logs, or an empty list if no logs.
        """
        try:
            where_fields = ()
            logs = Log.select()

            for field, value in kwargs.items():
                if field == "user_id":
                    where_fields += (Log.user_id == value,)
                    continue

                if field == "friendly_name":
                    where_fields += (getattr(Log, field).contains(value),)
                    continue

                if field[-3:] == "_at":
                    date_at = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").date()
                    start = datetime.combine(date_at, datetime.min.time())
                    end = datetime.combine(date_at, datetime.max.time())

                    where_fields += (getattr(Log, field).between(start, end),)
                    continue

                if hasattr(Log, field):
                    where_fields += (getattr(Log, field) == value,)
                    continue

                logger.warning("Field %s does not exist for logs model.", field)

            if sort and len(sort) > 0:
                sort_field = getattr(Log, sort[0])
                if sort[1] != "ASC":
                    sort_field = sort_field.desc()
                logs = logs.order_by(sort_field)

            if len(where_fields) > 0:
                logs = logs.where(*where_fields)

            total = logs.count()

            if data_range and len(data_range) > 0:
                limit = int(data_range[1])
                offset = int(data_range[0])
                logs = logs.offset(offset).limit(limit)

            logger.info("Successfully retrieved logs")

            return [total, list(logs)]

        except Exception as error:
            logger.error("Error retrieving logs.")
            raise error

    def delete_log(self, log_id: int) -> bool:
        """Delete a log by its ID.

        Args:
            log_id: The ID of the log to delete.

        Returns:
            True if the log was deleted, False otherwise.
        """
        try:
            log = self.get_log_by_id(log_id)
            if not log:
                logger.error("Log with ID %s does not exist.", log_id)
                return False

            log.delete_instance()

            logger.info("Log deleted successfully.")

            return True

        except Exception as error:
            logger.error("Error deleting log: %s", error)
            return False
