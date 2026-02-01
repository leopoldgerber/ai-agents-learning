import os
from typing import Any

import psycopg2
from psycopg2.extensions import connection as PgConnection


def build_db_conn(dsn: str) -> PgConnection:
    """Build a PostgreSQL connection.
    Args:
        dsn (str): PostgreSQL DSN connection string."""
    return psycopg2.connect(dsn)


def ensure_dedup_table(db_conn: PgConnection) -> None:
    """Ensure deduplication table exists.
    Args:
        db_conn (PgConnection): PostgreSQL connection."""
    create_sql = """
    CREATE TABLE IF NOT EXISTS webhook_dedup_events (
        event_id TEXT PRIMARY KEY,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with db_conn.cursor() as cursor:
        cursor.execute(create_sql)
    db_conn.commit()


def try_insert_event(db_conn: PgConnection, event_id: str) -> bool:
    """Try to insert event id into dedup table.
    Args:
        db_conn (PgConnection): PostgreSQL connection.
        event_id (str): Unique event identifier."""
    insert_sql = """
    INSERT INTO webhook_dedup_events (event_id)
    VALUES (%s)
    ON CONFLICT (event_id) DO NOTHING
    RETURNING event_id;
    """
    with db_conn.cursor() as cursor:
        cursor.execute(insert_sql, (event_id,))
        inserted_row = cursor.fetchone()

    db_conn.commit()
    return inserted_row is not None


def handle_event(
        db_conn: PgConnection, event_id: str, payload: dict[str, Any]) -> str:
    """Handle event with database-backed deduplication.
    Args:
        db_conn (PgConnection): PostgreSQL connection.
        event_id (str): Unique event identifier.
        payload (dict[str, Any]): Event payload."""
    is_first_delivery = try_insert_event(db_conn=db_conn, event_id=event_id)
    if not is_first_delivery:
        return 'duplicate'

    _ = payload
    return 'processed'


# === extra event deletion in db
def delete_event(db_conn: PgConnection, event_id: str) -> bool:
    """Delete deduplicated event by event id.
    Args:
        db_conn (PgConnection): PostgreSQL connection.
        event_id (str): Unique event identifier."""
    delete_sql = """
    DELETE FROM webhook_dedup_events
    WHERE event_id = %s
    RETURNING event_id;
    """
    with db_conn.cursor() as cursor:
        cursor.execute(delete_sql, (event_id,))
        deleted_row = cursor.fetchone()

    db_conn.commit()
    return deleted_row is not None


if __name__ == '__main__':
    dsn = os.getenv(
        'POSTGRES_DSN',
        "host=localhost port=5432 dbname=agent user=agent password=agent"
    )
    db_conn = build_db_conn(dsn=dsn)

    ensure_dedup_table(db_conn=db_conn)

    result_1 = handle_event(db_conn, 'evt_1', {'type': 'invoice.paid'})
    result_2 = handle_event(db_conn, 'evt_1', {'type': 'invoice.paid'})
    result_3 = handle_event(db_conn, 'evt_2', {'type': 'invoice.paid'})

    print(f'result_1 [evt_1]: {result_1}')
    print(f'result_2 [evt_1]: {result_2}')

    delete_event(db_conn=db_conn, event_id='evt_1')
    delete_event(db_conn=db_conn, event_id='evt_2')

    print(f'result_3 [evt_2]: {result_3}')

    db_conn.close()
