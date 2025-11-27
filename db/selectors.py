from typing import List, Tuple

from mysql.connector import MySQLConnection


def get_language_test_candidates(connection: MySQLConnection, max_rows: int = 20) -> List[Tuple]:
    """
    Fetch placeholder data for language test funnel candidates.

    This is a placeholder implementation used on Stage 1 to verify that:
    - Database connection works.
    - Queries can be executed without errors.

    In later stages this function will be replaced with a real query
    that selects users who:
    - passed a language test,
    - did not purchase a certificate,
    - were not yet added to the language funnel.
    """
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
    """
    Fetch placeholder data for non language test funnel candidates.

    Same idea as get_language_test_candidates:
    this is a temporary implementation that will be replaced later
    with real business logic.
    """
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
