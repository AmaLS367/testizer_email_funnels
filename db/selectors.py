from typing import List, Tuple

from mysql.connector import MySQLConnection


def get_language_test_candidates(connection: MySQLConnection, max_rows: int = 20) -> List[Tuple]:
    cursor = connection.cursor()

    query = """
    SELECT
        1 AS dummy_value,
        'language@example.com' AS dummy_email
    LIMIT %s
    """

    cursor.execute(query, (max_rows,))
    rows = cursor.fetchall()
    cursor.close()

    return rows


def get_non_language_test_candidates(connection: MySQLConnection, max_rows: int = 20) -> List[Tuple]:
    cursor = connection.cursor()

    query = """
    SELECT
        2 AS dummy_value,
        'non_language@example.com' AS dummy_email
    LIMIT %s
    """

    cursor.execute(query, (max_rows,))
    rows = cursor.fetchall()
    cursor.close()

    return rows
