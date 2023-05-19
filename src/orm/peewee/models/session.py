"""Peewee session model."""

from datetime import datetime
from uuid import uuid4

from peewee import Model, CharField, DateTimeField, TextField

from src.orm.peewee.connector import database


class Session(Model):
    """A model for the Session table."""

    sid = CharField(primary_key=True, default=uuid4)
    unique_identifier = CharField(null=True)
    user_agent = CharField(null=True)
    expires = DateTimeField(null=True)
    data = TextField(null=True)
    status = CharField(null=True)
    session_type = CharField(null=True)
    created_at = DateTimeField(null=True, default=datetime.now)

    class Meta:
        """A Meta class that specifies the database for the model."""

        database = database
        table_name = "sessions"


# Check if the table exists and create it if it doesn't
if not Session.table_exists():
    database.create_tables([Session])
