"""Peewee Handler for session model"""

import logging
from datetime import datetime, timedelta
import json
from typing import Optional

from src.orm.peewee.models.session import Session

from settings import Configurations

logger = logging.getLogger(__name__)


class SessionHandler:
    """
    A class for handling CRUD operations on the Session model.
    """

    def create_session(
        self, unique_identifier: str, user_agent: str, **kwargs
    ) -> Optional[Session]:
        """Create a new session.

        Args:
            unique_identifier (str): The identifier of the user creating the session.
            user_agent (str): The device of the user creating the session.
            kwargs: additional optional fields for the session model.

        Returns:
            The newly created session.
        """

        self.__clean__()

        max_age = Configurations.COOKIE_MAXAGE

        expires = str(datetime.now() + timedelta(milliseconds=max_age))

        cookie_data = {
            "max_age": max_age,
            "secure": Configurations.COOKIE_SECURE,
            "httponly": Configurations.COOKIE_HTTPONLY,
            "samesite": Configurations.COOKIE_SAMESITE,
        }

        try:
            session = Session.create(
                unique_identifier=unique_identifier,
                user_agent=user_agent,
                expires=expires,
                data=json.dumps(cookie_data),
                **kwargs
            )

            logger.info("Session created successfully.")

            return session

        except Exception as error:
            logger.error("Error creating session")
            raise error

    def get_session_by_field(self, **kwargs) -> Optional[Session]:
        """Retrieve a session by given field(s).

        Args:
            kwargs: fields for session to retrieve.

        Returns:
            The retrieved session, or None if no session found.
        """

        self.__clean__()

        try:
            get_fields = ()

            for field, value in kwargs.items():
                if hasattr(Session, field):
                    get_fields += (getattr(Session, field) == value,)
                else:
                    logger.warning("Field %s does not exist for session model.", field)

            session = Session.get(*get_fields)

            age = session.expires.timestamp() - datetime.now().timestamp()

            if age <= 0:
                logger.error("Session Expired")
                return None

            return session

        except Session.DoesNotExist:
            logger.error("Session not found.")
            return None

    def update_session(self, session_id: str) -> Optional[Session]:
        """Update an existing session.

        Args:
            session_id (str): The ID of the session to be updated.

        Returns:
            The updated session, or None if the session with the session_id does not exist.
        """

        self.__clean__()

        try:
            session = self.get_session_by_field(sid=session_id)
            if not session:
                logger.error("Session with ID %s does not exist.", session_id)
                return None

            max_age = Configurations.COOKIE_MAXAGE

            expires = str(datetime.now() + timedelta(milliseconds=max_age))

            cookie_data = {
                "max_age": max_age,
                "secure": Configurations.COOKIE_SECURE,
                "httponly": Configurations.COOKIE_HTTPONLY,
                "samesite": Configurations.COOKIE_SAMESITE,
            }

            session.data = json.dumps(cookie_data)
            session.expires = expires
            session.save()

            logger.info("Session updated successfully.")

            return session

        except Exception as error:
            logger.error("Error updating session")
            raise error

    def __clean__(self) -> None:
        """Remove all expired sessions"""

        sessions = Session.select()

        for session in sessions.iterator():
            age = session.expires.timestamp() - datetime.now().timestamp()

            if age <= 0:
                logger.debug("Removing expired session '%s' ...", session.sid)

                session.delete_instance()

        logger.info("Cleaning done")
