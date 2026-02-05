import os
import json
import psycopg2
from typing import Any
from dotenv import load_dotenv
load_dotenv()


def build_db_dsn() -> str:
    """Build Postgres DSN from environment variables.
    Args:
        None: No arguments."""
    dbname = os.getenv('DB_NAME', 'agent')
    user = os.getenv('DB_USER', 'agent')
    password = os.getenv('DB_PASSWORD', 'agent')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    return (
        f"dbname='{dbname}'"
        f"user='{user}'"
        f"password='{password}'"
        f"host='{host}'"
        f"port='{port}'"
    )


def ensure_tables(conn: psycopg2.extensions.connection) -> None:
    """Create users and idempotency_keys tables.
    Args:
        conn (psycopg2.extensions.connection): Open database connection."""
    users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    keys_sql = """
        CREATE TABLE IF NOT EXISTS idempotency_keys (
            request_id TEXT PRIMARY KEY,
            operation TEXT NOT NULL,
            response_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    with conn.cursor() as cur:
        cur.execute(users_sql)
        cur.execute(keys_sql)


def save_idempotency_response(
    conn: psycopg2.extensions.connection,
    request_id: str,
    operation: str,
    response_data: dict[str, Any],
) -> bool:
    """Save response for request_id,
    return True if saved, False if already exists.
    Args:
        conn (psycopg2.extensions.connection): Open database connection.
        request_id (str): Unique idempotency key from API client.
        operation (str): Operation name for debugging.
        response_data (dict[str, Any]): Response payload to store."""
    response_json = json.dumps(response_data, ensure_ascii=False)

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO idempotency_keys (request_id, operation, response_json)
            VALUES (%s, %s, %s)
            ON CONFLICT (request_id) DO NOTHING
            RETURNING request_id
            """,
            (request_id, operation, response_json),
        )
        row = cur.fetchone()
        return row is not None


def load_idempotency_response(
    conn: psycopg2.extensions.connection,
    request_id: str,
) -> dict[str, Any]:
    """Load stored response for request_id.
    Args:
        conn (psycopg2.extensions.connection): Open database connection.
        request_id (str): Unique idempotency key from API client."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT response_json
            FROM idempotency_keys
            WHERE request_id = %s
            """,
            (request_id,),
        )
        row = cur.fetchone()

    if row is None:
        return {'found': False}

    return {'found': True, 'response': json.loads(row[0])}


def create_user_response(
    conn: psycopg2.extensions.connection,
    email: str,
    name: str,
) -> dict[str, Any]:
    """Create a user idempotently and build API-like response.
    Args:
        conn (psycopg2.extensions.connection): Open database connection.
        email (str): User email.
        name (str): User name."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (email, name)
            VALUES (%s, %s)
            ON CONFLICT (email) DO NOTHING
            RETURNING id
            """,
            (email, name),
        )
        row = cur.fetchone()

    if row is None:
        return {'created': False, 'email': email}

    return {'created': True, 'email': email, 'user_id': row[0]}


def handle_create_user(
    conn: psycopg2.extensions.connection,
    request_id: str,
    email: str,
    name: str,
) -> dict[str, Any]:
    """Handle API-like request with request_id idempotency key.
    Args:
        conn (psycopg2.extensions.connection): Open database connection.
        request_id (str): Unique idempotency key from API client.
        email (str): User email.
        name (str): User name."""
    operation = 'create_user'

    with conn:
        response_data = create_user_response(conn=conn, email=email, name=name)
        saved = save_idempotency_response(
            conn=conn,
            request_id=request_id,
            operation=operation,
            response_data=response_data,
        )

        if saved:
            return {
                'source': 'computed',
                'request_id': request_id,
                'data': response_data
            }

        stored = load_idempotency_response(conn=conn, request_id=request_id)
        return {
            'source': 'stored',
            'request_id': request_id,
            'data': stored.get('response', {})
        }


def run_middle_demo(dsn: str) -> None:
    """Run middle idempotency demo with repeated request_id.
    Args:
        dsn (str): Postgres DSN string."""
    conn = psycopg2.connect(dsn)
    try:
        ensure_tables(conn=conn)

        request_id_value = 'req-001'
        email_value = 'jessica-1@example.com'
        name_value = 'Jessica-1'

        first = handle_create_user(
            conn=conn,
            request_id=request_id_value,
            email=email_value,
            name=name_value,
        )
        second = handle_create_user(
            conn=conn,
            request_id=request_id_value,
            email=email_value,
            name=name_value,
        )

        print({'first_call': first, 'second_call': second})
    finally:
        conn.close()


if __name__ == '__main__':
    dsn_value = build_db_dsn()
    run_middle_demo(dsn=dsn_value)
