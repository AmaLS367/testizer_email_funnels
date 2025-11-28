from typing import List, Tuple, Optional

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


def get_pending_funnel_entries(
    connection: MySQLConnection,
    max_rows: int = 100,
) -> List[Tuple]:
    cursor = connection.cursor()

    query = """
    SELECT
        email,
        funnel_type,
        user_id,
        test_id
    FROM funnel_entries
    WHERE certificate_purchased = 0
    ORDER BY entered_at ASC
    LIMIT %s
    """

    cursor.execute(query, (max_rows,))
    rows = cursor.fetchall()
    cursor.close()

    return rows


def get_certificate_purchase_for_entry(
    connection: MySQLConnection,
    email: str,
    user_id: Optional[int],
    test_id: Optional[int],
) -> Optional[Tuple]:
    cursor = connection.cursor()

    query = """
    SELECT
        o.id AS order_id,
        o.created_at AS purchased_at
    FROM orders AS o
    WHERE
        o.email = %s
        AND o.is_certificate = 1
        AND o.status IN ('paid', 'completed')
    ORDER BY o.created_at DESC
    LIMIT 1
    """

    params = (email,)

    cursor.execute(query, params)
    row = cursor.fetchone()
    cursor.close()

    return row
