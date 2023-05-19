"""Peewee log model."""

from datetime import datetime

from peewee import Model, CharField, DateTimeField, TextField, ForeignKeyField

from src.orm.peewee.connector import database
from src.orm.peewee.models.user import User


class Log(Model):
    """A model for the log table."""

    sid = CharField()
    service_id = CharField(null=True)
    service_name = CharField(null=True)
    project_reference = CharField(null=True)
    direction = CharField(null=True)
    to = CharField(null=True)
    from_ = CharField(null=True)
    status = CharField(null=True)
    channel = CharField(null=True)
    reason = TextField(null=True)
    user_id = ForeignKeyField(User)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        """A Meta class that specifies the database for the model."""

        database = database
        table_name = "logs"


# Check if the table exists and create it if it doesn't
if not Log.table_exists():
    database.create_tables([Log])
