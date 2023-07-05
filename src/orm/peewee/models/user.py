"""Peewee user models."""

from datetime import datetime

from peewee import Model, CharField, DateTimeField

from src.orm.peewee.connector import database


class User(Model):
    """A model for the User table."""

    account_sid = CharField(unique=True)
    auth_token = CharField()
    email = CharField(unique=True)
    password = CharField()
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    phone_number = CharField(null=True)
    twilio_account_sid = CharField(null=True)
    twilio_auth_token = CharField(null=True)
    twilio_service_sid = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        """A Meta class that specifies the database for the model."""

        database = database
        table_name = "users"


# Check if the table exists and create it if it doesn't
if not User.table_exists():
    database.create_tables([User])
