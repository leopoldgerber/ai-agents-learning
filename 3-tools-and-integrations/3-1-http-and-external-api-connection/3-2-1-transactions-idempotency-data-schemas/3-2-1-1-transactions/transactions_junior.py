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
            action TEXT NOT NULL
        );
    """

    with conn.cursor() as cur:
        cur.execute(create_users_sql)
        cur.execute(create_logs_sql)


def create_user_with_log(
        conn: psycopg2.extensions.connection,
        name: str,
        email: str
) -> None:
    """Insert a user and a log record in a single transaction.
    Args:
        conn (psycopg2.extensions.connection): Open database connection.
        name (str): User name.
        email (str): User email."""
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO users (name, email) VALUES (%s, %s)',
                (name, email),
            )
            cur.execute(
                'INSERT INTO logs (action) VALUES (%s)',
                (f'User created: {email}',),
            )


def run_junior_demo(dsn: str) -> None:
    """Run a minimal transaction demo.
    Args:
        dsn (str): Postgres DSN string."""
    conn = psycopg2.connect(dsn)
    try:
        ensure_tables(conn=conn)
        create_user_with_log(conn=conn, name='Alex', email='alex@example.com')
        print('OK: transaction committed')
    except Exception as exc:
        print('ERROR: transaction rolled back:', exc)
    finally:
        conn.close()


if __name__ == '__main__':
    dsn_value = build_db_dsn()
    run_junior_demo(dsn=dsn_value)
