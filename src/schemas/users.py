"""Peewee Users Model"""

from datetime import datetime

from peewee import Model, AutoField, CharField, DateTimeField

from src.schemas.db_connector import connection


class Users(Model):
    """Model definition"""

    id = AutoField()
    email = CharField()
    email_hash = CharField(unique=True)
    password = CharField()
    name = CharField(null=True)
    phone_number = CharField(null=True)
    account_sid = CharField()
    auth_token = CharField()
    twilio_account_sid = CharField(null=True)
    twilio_auth_token = CharField(null=True)
    twilio_service_sid = CharField(null=True)
    created_at = DateTimeField(default=datetime.now)
    iv = CharField()

    class Meta:
        """Meta definition"""

        database = connection


if not connection.table_exists("users"):
    connection.create_tables([Users])
