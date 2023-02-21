"""Peewee Sessions Model"""

from datetime import datetime
from uuid import uuid4

from peewee import Model, CharField, DateTimeField, TextField

from src.schemas.db_connector import connection


class Sessions(Model):
    """Model definition"""

    sid = CharField(primary_key=True, default=uuid4)
    unique_identifier = CharField(null=True)
    user_agent = CharField(null=True)
    expires = DateTimeField(null=True)
    data = TextField(null=True)
    status = CharField(null=True)
    session_type = CharField(null=True)
    created_at = DateTimeField(null=True, default=datetime.now)

    class Meta:
        """Meta definition"""

        database = connection


if not connection.table_exists("sessions"):
    connection.create_tables([Sessions])
