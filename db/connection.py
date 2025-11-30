import logging
import time
from contextlib import contextmanager
from typing import Generator, Optional

import mysql.connector
from mysql.connector import MySQLConnection

from config.settings import DatabaseSettings


# Module-level connection for lazy reuse
_active_connection: Optional[MySQLConnection] = None

logger = logging.getLogger("db.connection")


def create_database_connection(
    database_settings: DatabaseSettings,
    connection_timeout: int = 10,
    read_timeout: int = 30,
    write_timeout: int = 30,
) -> MySQLConnection:
    """Creates a new MySQL database connection with timeouts and reconnect logic.

    Establishes a connection to the MODX database using credentials from settings.
    The connection includes explicit timeouts and automatic retry on connection failures.
    The connection must be explicitly closed by the caller to prevent resource leaks.

    Args:
        database_settings: Configuration object containing database credentials.
        connection_timeout: Timeout in seconds for establishing the connection.
            Defaults to 10.
        read_timeout: Timeout in seconds for read operations. Defaults to 30.
        write_timeout: Timeout in seconds for write operations. Defaults to 30.

    Returns:
        Active MySQL connection object. Caller is responsible for closing it.

    Raises:
        mysql.connector.Error: If connection fails after retry attempts due to
            invalid credentials, network issues, or database unavailability.
    """
    attempt_count = 0
    max_attempts = 2

    while attempt_count < max_attempts:
        try:
            connection = mysql.connector.connect(
                host=database_settings.host,
                port=database_settings.port,
                user=database_settings.user,
                password=database_settings.password,
                database=database_settings.name,
                charset=database_settings.charset,
                connection_timeout=connection_timeout,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
            )

            return connection  # type: ignore[return-value]

        except mysql.connector.Error as error:
            error_message = str(error).lower()
            is_connection_error = (
                "server has gone away" in error_message
                or "connection refused" in error_message
                or "can't connect" in error_message
            )

            if is_connection_error and attempt_count < max_attempts - 1:
                attempt_count += 1
                logger.warning(
                    "Database connection failed (attempt %d/%d): %s. Retrying in 2 seconds...",
                    attempt_count,
                    max_attempts,
                    error,
                )
                time.sleep(2)
            else:
                # Not a connection error or all attempts exhausted
                raise

    # This should never be reached, but mypy needs it
    raise mysql.connector.Error("Failed to establish database connection")


def _get_or_create_connection(
    database_settings: DatabaseSettings,
) -> MySQLConnection:
    """Gets the active connection or creates a new one if none exists.

    Args:
        database_settings: Configuration object containing database credentials.

    Returns:
        Active MySQL connection object.
    """
    global _active_connection

    if _active_connection is None:
        _active_connection = create_database_connection(database_settings)

    return _active_connection


def _reset_connection() -> None:
    """Closes and resets the active connection."""
    global _active_connection

    if _active_connection is not None:
        try:
            _active_connection.close()
        except Exception:
            # Ignore errors when closing a broken connection
            pass
        _active_connection = None


@contextmanager
def database_connection_scope(
    database_settings: DatabaseSettings,
) -> Generator[MySQLConnection, None, None]:
    """Context manager for database connections with lazy reuse and automatic cleanup.

    Reuses a single module-level connection across scopes. If the connection is lost
    (e.g., "server has gone away"), it is automatically reset and a new connection
    is created on the next scope entry.

    The connection is not closed on scope exit - it remains available for reuse.
    Transaction boundaries (commit/rollback) are managed by the caller.

    Args:
        database_settings: Configuration object containing database credentials.

    Yields:
        Active MySQL connection object.

    Example:
        ```python
        with database_connection_scope(settings.database) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.commit()
        # Connection remains open for reuse
        ```
    """
    connection = _get_or_create_connection(database_settings)

    try:
        yield connection
    except mysql.connector.Error as error:
        error_message = str(error).lower()
        if "server has gone away" in error_message:
            logger.warning(
                "Database connection lost during operation: %s. Resetting connection.",
                error,
            )
            _reset_connection()
        raise
