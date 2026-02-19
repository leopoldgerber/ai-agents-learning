import sqlite3
from dataclasses import dataclass
from typing import List, Set, Tuple


ALLOWED_TABLES: Set[str] = {"users", "orders", "products"}
ALLOWED_COLUMNS: Set[str] = {"id", "name", "email", "created_at"}


@dataclass(frozen=True)
class QueryResult:
    rows: List[Tuple]
    query: str


def safe_select_by_id(
    conn: sqlite3.Connection,
    table_name: str,
    id_column: str,
    user_id: int,
) -> QueryResult:
    """
    Safe SELECT:
    - identifiers validated via whitelist
    - values passed via parameterization
    """
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table_name}")

    if id_column not in ALLOWED_COLUMNS:
        raise ValueError(f"Invalid column: {id_column}")

    query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
    cur = conn.cursor()
    cur.execute(query, (user_id,))
    return QueryResult(rows=cur.fetchall(), query=query)


def unsafe_select_by_id(
    conn: sqlite3.Connection,
    table_name: str,
    user_id: int,
) -> List[Tuple]:
    """
    Unsafe SELECT example (do not use):
    identifier is injected directly.
    """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name} WHERE id = ?", (user_id,))
    return cur.fetchall()


def setup_demo_db(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT, email TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
    conn.commit()


def main() -> None:
    conn = sqlite3.connect(":memory:")
    setup_demo_db(conn)

    ok = safe_select_by_id(conn, "users", "id", 1)
    print("SAFE query:", ok.query)
    print("SAFE rows:", ok.rows)

    try:
        safe_select_by_id(conn, "users; DROP TABLE users--", "id", 1)
    except ValueError as exc:
        print("Blocked injection attempt:", exc)

    conn.close()


if __name__ == "__main__":
    main()
