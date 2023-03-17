"""Peewee Logs Model"""

from datetime import datetime

from peewee import Model, CharField, DateTimeField, TextField, ForeignKeyField

from src.schemas.users import Users
from src.schemas.db_connector import connection


class Logs(Model):
    """Model definition"""

    sid = CharField(primary_key=True)
    service = CharField()
    service_name = CharField(null=True)
    project_ref = CharField()
    direction = CharField(null=True)
    to = CharField()
    from_ = CharField(null=True)
    status = CharField()
    channel = CharField(null=True)
    reason = TextField(null=True)
    user_id = ForeignKeyField(Users)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        """Meta definition"""

        database = connection


if not connection.table_exists("logs"):
    connection.create_tables([Logs])
