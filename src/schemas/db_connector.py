"""Peewee Base Model"""

import logging
from contextlib import closing

from peewee import MySQLDatabase, DatabaseError
from mysql.connector import connect

from settings import Configurations

MYSQL_HOST = Configurations.MYSQL_HOST
MYSQL_USER = Configurations.MYSQL_USER
MYSQL_PASSWORD = Configurations.MYSQL_PASSWORD
MYSQL_DATABASE = Configurations.MYSQL_DATABASE

logger = logging.getLogger(__name__)

try:
    with closing(
        connect(
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            host=MYSQL_HOST,
            auth_plugin="mysql_native_password",
        )
    ) as connection:
        query = f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}"

        with closing(connection.cursor()) as cursor:
            cursor.execute(query)

except Exception as error:
    logger.error("[!] Error creating database. See logs below")
    raise error

try:
    connection = MySQLDatabase(
        database=MYSQL_DATABASE,
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
    )

except DatabaseError as error:
    logger.error("[!] Error connecting to database. See logs below")
    raise error
