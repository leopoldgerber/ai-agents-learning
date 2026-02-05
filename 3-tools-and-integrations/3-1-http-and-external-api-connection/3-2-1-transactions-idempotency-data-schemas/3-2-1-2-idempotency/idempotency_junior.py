import os
import psycopg2
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


def ensure_users_table(conn: psycopg2.extensions.connection) -> None:
    """Create users table with UNIQUE email constraint.
    Args:
        conn (psycopg2.extensions.connection): Open database connection."""
    sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    with conn.cursor() as cur:
        cur.execute(sql)


def create_user_if_not_exists(
    conn: psycopg2.extensions.connection,
    email: str,
    name: str,
) -> bool:
    """Create user idempotently using ON CONFLICT DO NOTHING.
    Args:
        conn (psycopg2.extensions.connection): Open database connection.
        email (str): User email used as idempotency key.
        name (str): User display name."""
    with conn:
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
            return row is not None


def run_junior_demo(dsn: str) -> None:
    """Run junior idempotency demo with repeated 'API' calls.
    Args:
        dsn (str): Postgres DSN string."""
    conn = psycopg2.connect(dsn)
    try:
        ensure_users_table(conn=conn)

        email_value = 'joe@example.com'
        name_value = 'Joe'

        first_created = create_user_if_not_exists(
            conn=conn,
            email=email_value,
            name=name_value
        )
        second_created = create_user_if_not_exists(
            conn=conn,
            email=email_value,
            name=name_value
        )

        print(
            {
                'first_call_created': first_created,
                'second_call_created': second_created
            }
        )
    finally:
        conn.close()


if __name__ == '__main__':
    dsn_value = build_db_dsn()
    run_junior_demo(dsn=dsn_value)
