from contextlib import contextmanager
from typing import Generator

import mysql.connector
from mysql.connector import MySQLConnection

from config.settings import DatabaseSettings


def create_database_connection(database_settings: DatabaseSettings) -> MySQLConnection:
    """
    Create a new MySQL database connection.
    """
    connection = mysql.connector.connect(
        host=database_settings.host,
        port=database_settings.port,
        user=database_settings.user,
        password=database_settings.password,
        database=database_settings.name,
        charset=database_settings.charset,
    )

    return connection


@contextmanager
def database_connection_scope(database_settings: DatabaseSettings) -> Generator[MySQLConnection, None, None]:
    """
    Context manager that creates and closes a database connection.
    """
    connection = create_database_connection(database_settings)

    try:
        yield connection
    finally:
        connection.close()
