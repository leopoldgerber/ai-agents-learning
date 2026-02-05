import os

from dotenv import load_dotenv
import psycopg2


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
        f"port='{port}' "
    )


def drop_users_table(conn: psycopg2.extensions.connection) -> None:
    """Drop users table.
    Args:
        conn (psycopg2.extensions.connection): Open database connection."""
    sql = """
        DROP TABLE IF EXISTS users;
    """

    with conn.cursor() as cur:
        cur.execute(sql)


def ensure_users_table(conn: psycopg2.extensions.connection) -> None:
    """Create users table with UNIQUE constraint.
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


def insert_user_once(
    conn: psycopg2.extensions.connection,
    email: str,
    name: str,
) -> bool:
    """Insert user once, return True if inserted, False if already exists.
    Args:
        conn (psycopg2.extensions.connection): Open database connection.
        email (str): User email (unique key).
        name (str): User name."""
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


def run_schema_demo(dsn: str) -> dict[str, bool]:
    """Run schema demo: two inserts where first is True and second is False.
    Args:
        dsn (str): Postgres DSN string."""
    conn = psycopg2.connect(dsn)
    try:
        drop_users_table(conn=conn)
        ensure_users_table(conn=conn)

        email_value = 'alex@example.com'
        name_value = 'Alex'

        first_result = insert_user_once(
            conn=conn,
            email=email_value,
            name=name_value
        )
        second_result = insert_user_once(
            conn=conn,
            email=email_value,
            name=name_value
        )

        return {'first_insert': first_result, 'second_insert': second_result}
    finally:
        conn.close()


if __name__ == '__main__':
    dsn_value = build_db_dsn()
    demo_result = run_schema_demo(dsn=dsn_value)
    print(demo_result)
