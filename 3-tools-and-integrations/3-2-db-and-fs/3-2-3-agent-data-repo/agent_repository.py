import json
from typing import Any, Dict, Optional

import psycopg2
import redis


class AgentRepository:
    """Repository for managing agent data with PostgreSQL
    as the primary storage and Redis as a caching layer."""

    def __init__(
            self,
            db_config: Dict[str, Any],
            redis_config: Dict[str, Any]
    ):
        self.connection = psycopg2.connect(**db_config)
        self.redis_client = redis.Redis(**redis_config)

    def get_agent(self, agent_id: int) -> Optional[Dict[str, Any]]:
        cache_key = f"agent:{agent_id}"

        # Check cache
        cached_agent = self.redis_client.get(cache_key)
        if cached_agent:
            return json.loads(cached_agent)

        # Query the database
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, email FROM agents WHERE id = %s",
                (agent_id,)
            )
            row = cursor.fetchone()

            if row:
                agent = {"id": row[0], "name": row[1], "email": row[2]}
                # Cache the result with TTL
                self.redis_client.setex(cache_key, 60, json.dumps(agent))
                return agent

        return None

    def create_agent(self, agent_data: Dict[str, Any]) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO agents (name, email) VALUES (%s, %s)",
                (agent_data["name"], agent_data["email"])
            )
        self.connection.commit()

    def update_agent(self, agent_id: int, agent_data: Dict[str, Any]) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE agents SET name = %s, email = %s WHERE id = %s",
                (agent_data["name"], agent_data["email"], agent_id)
            )
        self.connection.commit()
        # Cache invalidation
        self.redis_client.delete(f"agent:{agent_id}")

    def delete_agent(self, agent_id: int) -> None:
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM agents WHERE id = %s", (agent_id,))
        self.connection.commit()
        # Cache removal
        self.redis_client.delete(f"agent:{agent_id}")


def close_repository(repo: AgentRepository) -> bool:
    """Close database and cache connections.
    Args:
        repo (AgentRepository): Repository instance."""
    repo.connection.close()
    try:
        repo.redis_client.close()
    except Exception:
        pass
    return True
