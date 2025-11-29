from datetime import datetime
from typing import List, Tuple, Optional

from mysql.connector import MySQLConnection


DEFAULT_CANDIDATE_LOOKBACK_DAYS = 30


def get_language_test_candidates(
    connection: MySQLConnection,
    limit: int = 100,
) -> List[Tuple[int, str]]:
    cursor = connection.cursor()

    query = """
    SELECT
        u.Id AS user_id,
        u.Email AS email
    FROM simpletest_users AS u
    INNER JOIN simpletest_test AS t
        ON t.Id = u.TestId
    INNER JOIN simpletest_lang AS l
        ON l.Id = t.LangId
    LEFT JOIN funnel_entries AS f
        ON f.email = u.Email
       AND f.funnel_type = %s
    WHERE
        u.Email IS NOT NULL
        AND u.Email <> ''
        AND u.Datep >= DATE_SUB(NOW(), INTERVAL %s DAY)
        AND f.id IS NULL
    ORDER BY
        u.Datep DESC
    LIMIT %s
    """

    params = ("language", DEFAULT_CANDIDATE_LOOKBACK_DAYS, limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()

    return rows


def get_non_language_test_candidates(
    connection: MySQLConnection,
    limit: int = 100,
) -> List[Tuple[int, str]]:
    return []


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
    funnel_type: str,
    user_id: Optional[int],
    test_id: Optional[int],
) -> Optional[Tuple[int, datetime]]:
    query = """
    SELECT
        p.id,
        p.datetime_payment
    FROM modx_cert_payment AS p
    INNER JOIN modx_cert_result AS r ON r.id = p.id_result
    INNER JOIN modx_cert_users AS u ON u.id = r.id_user
    INNER JOIN modx_cert_test AS t ON t.id = r.id_test
    WHERE
        u.email = %(email)s
        AND p.id_status = 2
        AND p.datetime_payment IS NOT NULL
        AND (
            (%(funnel_type)s = 'language' AND t.type = 1)
            OR (%(funnel_type)s = 'non_language' AND t.type = 2)
        )
    ORDER BY p.datetime_payment ASC
    LIMIT 1
    """

    params = {
        "email": email,
        "funnel_type": funnel_type,
    }

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        row = cursor.fetchone()

    if row is None:
        return None

    payment_id, payment_datetime = row

    return int(payment_id), payment_datetime


def get_funnel_conversion_summary(connection, from_date, to_date):
    query = """
    SELECT
        funnel_type,
        COUNT(*) AS total_entries,
        SUM(CASE WHEN certificate_purchased = 1 THEN 1 ELSE 0 END) AS total_purchased
    FROM funnel_entries
    WHERE 1 = 1
    """

    params = {}

    if from_date is not None:
        query += " AND entered_at >= %(from_date)s"
        params["from_date"] = from_date

    if to_date is not None:
        query += " AND entered_at < %(to_date)s"
        params["to_date"] = to_date

    query += " GROUP BY funnel_type ORDER BY funnel_type"

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    result = []

    for row in rows:
        funnel_type, total_entries, total_purchased = row
        result.append(
            (
                str(funnel_type),
                int(total_entries),
                int(total_purchased),
            )
        )

    return result
