import os
import time
from typing import Optional

import psycopg2
from psycopg2 import errors
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
        f"dbname='{dbname}' "
        f"user='{user}' "
        f"password='{password}' "
        f"host='{host}' "
        f"port='{port}'"
    )


def ensure_tables(conn: psycopg2.extensions.connection) -> None:
    """Create tables if they do not exist.
    Args:
        conn (psycopg2.extensions.connection): Open database connection."""
    create_users_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        );
    """
    create_logs_sql = """
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            action TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    with conn.cursor() as cur:
        cur.execute(create_users_sql)
        cur.execute(create_logs_sql)


def try_create_user_with_log(
    conn: psycopg2.extensions.connection,
    name: str,
    email: str,
    request_id: str,
) -> None:
    """Insert user and log within an explicit transaction.
    Args:
        conn (psycopg2.extensions.connection): Open database connection.
        name (str): User name.
        email (str): User email.
        request_id (str): Correlation id for logs."""
    conn.autocommit = False
    conn.set_session(isolation_level='SERIALIZABLE')

    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO users (name, email) VALUES (%s, %s)',
                (name, email),
            )
            cur.execute(
                'INSERT INTO logs (action) VALUES (%s)',
                (f'request_id={request_id} user_created email={email}',),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def create_user_with_retry(
    dsn: str,
    name: str,
    email: str,
    request_id: str,
    max_attempts: int,
    base_sleep_seconds: float,
) -> Optional[str]:
    """Create a user with retry on serialization failures.
    Args:
        dsn (str): Postgres DSN string.
        name (str): User name.
        email (str): User email.
        request_id (str): Correlation id for logs.
        max_attempts (int): Max retry attempts.
        base_sleep_seconds (float): Base delay between retries."""
    attempt_index = 0
    last_error: Optional[str] = None

    while attempt_index < max_attempts:
        conn = psycopg2.connect(dsn)
        try:
            ensure_tables(conn=conn)
            try_create_user_with_log(
                conn=conn,
                name=name,
                email=email,
                request_id=request_id
            )
            return None
        except errors.SerializationFailure as exc:
            last_error = str(exc)
            time.sleep(base_sleep_seconds * (attempt_index + 1))
        except Exception as exc:
            last_error = str(exc)
            return last_error
        finally:
            conn.close()

        attempt_index += 1

    return last_error


def run_middle_demo(dsn: str) -> None:
    """Run a middle-level transaction demo with retries.
    Args:
        dsn (str): Postgres DSN string."""
    error_text = create_user_with_retry(
        dsn=dsn,
        name='Jessica',
        email='jessica@example.com',
        request_id='req-001',
        max_attempts=3,
        base_sleep_seconds=0.2,
    )

    if error_text is None:
        print('OK: transaction committed')
    else:
        print('ERROR:', error_text)


if __name__ == '__main__':
    dsn_value = build_db_dsn()
    run_middle_demo(dsn=dsn_value)
