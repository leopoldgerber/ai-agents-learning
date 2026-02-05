import os
from typing import Any, Dict

import psycopg2
from dotenv import load_dotenv

from agent_repository import AgentRepository, close_repository
from agent_service import (
    create_agent_with_limit,
    delete_agent_profile,
    get_agent_or_error,
    update_agent_profile,
)


load_dotenv()


def build_db_config() -> Dict[str, Any]:
    """Build psycopg2 config dict from environment variables.
    Args:
        None: No arguments."""
    dbname = os.getenv('DB_NAME', 'agent')
    user = os.getenv('DB_USER', 'agent')
    password = os.getenv('DB_PASSWORD', 'agent')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    return {
        'dbname': dbname,
        'user': user,
        'password': password,
        'host': host,
        'port': port
    }


def build_redis_config() -> Dict[str, Any]:
    """Build redis-py config dict from environment variables.
    Args:
        None: No arguments."""
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', '6379'))
    db_index = int(os.getenv('REDIS_DB', '0'))
    password = os.getenv('REDIS_PASSWORD')

    config: Dict[str, Any] = {'host': host, 'port': port, 'db': db_index}
    if password:
        config['password'] = password

    return config


def ensure_agents_table(db_config: Dict[str, Any]) -> bool:
    """Create agents table if it does not exist.
    Args:
        db_config (dict[str, Any]): psycopg2 connection kwargs."""
    sql = """
        CREATE TABLE IF NOT EXISTS agents (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        );
    """

    conn = psycopg2.connect(**db_config)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql)
        return True
    finally:
        conn.close()


def run_demo() -> Dict[str, Any]:
    """Run orchestrated demo for repository + service layers.
    Args:
        None: No arguments."""
    db_config = build_db_config()
    redis_config = build_redis_config()

    ensure_agents_table(db_config=db_config)

    repo = AgentRepository(db_config=db_config, redis_config=redis_config)
    try:
        create_result = create_agent_with_limit(
            repo=repo,
            agent_data={'name': 'Alex', 'email': 'alex@example.com'},
            max_agents_per_email=2,
        )

        first_read = get_agent_or_error(repo=repo, agent_id=1)
        second_read = get_agent_or_error(repo=repo, agent_id=1)

        update_result = update_agent_profile(
            repo=repo,
            agent_id=1,
            agent_data={'name': 'Jessica', 'email': 'alex@example.com'},
        )

        third_read = get_agent_or_error(repo=repo, agent_id=1)

        delete_result = delete_agent_profile(repo=repo, agent_id=1)
        after_delete = get_agent_or_error(repo=repo, agent_id=1)

        return {
            'create': create_result,
            'first_read': first_read,
            'second_read': second_read,
            'update': update_result,
            'third_read': third_read,
            'delete': delete_result,
            'after_delete': after_delete,
        }
    finally:
        close_repository(repo=repo)


if __name__ == '__main__':
    result_data = run_demo()
    print(result_data)
