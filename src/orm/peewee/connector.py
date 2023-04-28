"""Peewee connector"""

from contextlib import closing

from peewee import MySQLDatabase
import mysql.connector

from settings import Configurations

MYSQL_HOST = Configurations.MYSQL_HOST
MYSQL_USER = Configurations.MYSQL_USER
MYSQL_PASSWORD = Configurations.MYSQL_PASSWORD
MYSQL_DATABASE = Configurations.MYSQL_DATABASE


def create_database_if_not_exists(
    user: str, password: str, host: str, database_name: str
) -> None:
    """
    Creates a database if it doesn't exist.

    Parameters:
        user (str): database user.
        password (str): database password.
        host (str): database host.
        database_name (str): database name.

    Returns:
        None.
    """
    # MySQL
    with closing(
        mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            auth_plugin="mysql_native_password",
        )
    ) as connection:
        query = f"CREATE DATABASE IF NOT EXISTS {database_name}"

        with closing(connection.cursor()) as cursor:
            cursor.execute(query)


# Connect to the MySQL database using Peewee
create_database_if_not_exists(
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    database_name=MYSQL_DATABASE,
)

database = MySQLDatabase(
    MYSQL_DATABASE, user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST
)
