"""Peewee project model."""

from datetime import datetime

from peewee import Model, CharField, DateTimeField, ForeignKeyField

from src.orm.peewee.connector import database
from src.orm.peewee.models.user import User


class Project(Model):
    """A model for the Project table."""

    reference = CharField(null=True)
    friendly_name = CharField()
    user_id = ForeignKeyField(User)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        """A Meta class that specifies the database for the model."""

        database = database
        table_name = "projects"


# Check if the table exists and create it if it doesn't
if not Project.table_exists():
    database.create_tables([Project])
