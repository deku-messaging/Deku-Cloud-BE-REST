"""Session Handler"""

import logging
import json
from datetime import datetime, timedelta

from werkzeug.exceptions import (
    Unauthorized
)

from src.schemas.sessions import Sessions

from settings import Configurations

SECURE_COOKIE = Configurations.SECURE_COOKIE

logger = logging.getLogger(__name__)

class SessionModel:
    """Handler definition"""
    def __init__(self, session_lifetime: str) -> None:
        """
        """
        self.sessions = Sessions
        self.session_lifetime = session_lifetime
        self.cookie_data = {
            "maxAge": self.session_lifetime,
            "expires": str(datetime.now() + timedelta(milliseconds=self.session_lifetime)),
            "secure": SECURE_COOKIE,
            "httpOnly": True,
            "sameSite": "lax",
        }

    def __clean__(self) -> None:
        """Update expired session's status"""
        sessions = self.sessions.select()

        for session in sessions.iterator():
            age = session.expires.timestamp() - datetime.now().timestamp()

            if age <= 0:
                logger.debug("[*] Removing expired session '%s' ...", session.sid)

                session.delete_instance()

        logger.info("[x] Cleaning done")

    def create(
        self,
        unique_identifier: str,
        user_agent: str,
        status: str = None,
        session_type: str = None) -> object:
        """
        Create session in database.

        Keyword arguments:
        unique_identifier -- Session's owner,
        user_agent -- Device consumming session,
        status -- Session's status,
        session_type -- Type of session

        return: object
        """

        self.__clean__()

        try:
            logger.debug("[*] Creating session for %s ...", unique_identifier)

            session = self.sessions.create(
                unique_identifier=unique_identifier,
                user_agent=user_agent,
                expires=self.cookie_data["expires"],
                data=json.dumps(self.cookie_data),
                status=status,
                session_type=session_type
            )

        except Exception as error:
            logger.error("[!] Error creating session. See logs below")
            raise error

        else:
            logger.info("[x] Successfully created session")
            return session

    def find(
        self,
        sid: str,
        user_agent: str,
        status: str = None,
        session_type: str = None) -> object:
        """
        Find session in database.

        Keyword arguments:
        sid -- Session's unique ID,
        user_agent -- Device consumming session,
        status -- Session's status,
        session_type -- Type of session

        return: object
        """

        self.__clean__()

        try:
            logger.debug("[*] Finding session '%s' ...", sid)

            session = self.sessions.get(
                self.sessions.sid == sid,
                self.sessions.user_agent == user_agent,
                self.sessions.status == status,
                self.sessions.session_type == session_type
            )

        except self.sessions.DoesNotExist as error:
            logger.error("[!] Session not Found")
            raise Unauthorized() from error

        else:
            logger.debug("[*] Checking status ...")

            age = session.expires.timestamp() - datetime.now().timestamp()

            if age <= 0:
                logger.error("[!] Session Expired")
                raise Unauthorized()

            logger.info("[x] Session Found")

            return session

    def update(
        self,
        sid: str,
        user_agent: str,
        session_type: str = None) -> object:
        """
        Update session in database.

        Keyword arguments:
        sid -- Session's unique ID,
        user_agent -- Device consumming session,
        status -- Session's status,
        session_type -- Type of session

        return: object
        """

        self.__clean__()

        try:
            logger.debug("[*] Finding session '%s' ...", sid)

            session = self.sessions.get(
                self.sessions.sid == sid,
                self.sessions.user_agent == user_agent,
                self.sessions.session_type == session_type
            )

        except self.sessions.DoesNotExist as error:
            logger.error("[!] Session not Found")
            raise Unauthorized() from error

        else:
            logger.debug("[*] Updaing session '%s' ...", session.sid)

            session.data = json.dumps(self.cookie_data)
            session.expires = self.cookie_data["expires"]

            session.save()

            logger.info("[x] Session Updated")

            return session
