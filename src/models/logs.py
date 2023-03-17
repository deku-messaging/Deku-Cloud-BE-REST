"""Logs Handler"""

import logging

from uuid import uuid4

from src.schemas.logs import Logs

logger = logging.getLogger(__name__)


class LogModel:
    """Handler definition"""

    def __init__(self) -> None:
        self.logs = Logs

    def create(
        self,
        service: str,
        pid: str,
        to_: str,
        status: str,
        user_id: str,
        from_: str = None,
        sid: str = None,
        channel: str = None,
        serivce_name: str = None,
        reason: str = None,
        direction: str = None,
    ) -> object:
        """Create log.

        Keyword arguments:
        sid -- identifier
        service -- provided service
        pid -- project's reference
        serivce_name -- service_name(queue_name)
        to_ -- recipient
        from_ -- sender
        status -- current status
        user_id -- authenticated user's ID
        reason -- reason for log
        direction -- direction of service (outbound-api or inbound-api)
        """
        if not sid:
            sid = str(uuid4())

        try:
            log = self.logs.create(
                sid=sid,
                service=service,
                project_ref=pid,
                serivce_name=serivce_name,
                direction=direction,
                to=to_,
                from_=from_,
                status=status,
                channel=channel,
                reason=reason,
                user_id=user_id,
            )

            logger.info("[x] Successfully created log.")

            return log

        except Exception as error:
            logger.error("[!] Error creating log. See logs below.")
            raise error
