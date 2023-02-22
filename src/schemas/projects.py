"""Peewee Projects Model"""

from datetime import datetime

from peewee import Model, AutoField, CharField, DateTimeField, ForeignKeyField

from src.schemas.db_connector import connection
from src.schemas.users import Users


class Projects(Model):
    """Model definition"""

    id = AutoField()
    project_ref = CharField(null=True)
    name = CharField()
    user_id = ForeignKeyField(Users)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        """Meta definition"""

        database = connection
        indexes = ((('name', 'user_id'), True),)


if not connection.table_exists("projects"):
    connection.create_tables([Projects])
