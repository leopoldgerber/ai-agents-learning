import os
import time
from typing import Any

import redis
from dotenv import load_dotenv


load_dotenv()


def build_redis_client() -> redis.Redis:
    """Build Redis client from environment variables.
    Args:
        None: No arguments."""
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', '6379'))
    db_index = int(os.getenv('REDIS_DB', '0'))
    password = os.getenv('REDIS_PASSWORD')

    if password:
        return redis.Redis(
            host=host,
            port=port,
            db=db_index,
            password=password
        )

    return redis.Redis(host=host, port=port, db=db_index)


def build_rate_limit_key(client_id: str) -> str:
    """Build Redis key for rate limiting.
    Args:
        client_id (str): Client identifier."""
    return f'rate_limit:{client_id}'


def check_rate_limit(
    redis_client: redis.Redis,
    client_id: str,
    limit: int,
    window_seconds: int,
) -> dict[str, Any]:
    """Check and update rate limit counter.
    Args:
        redis_client (redis.Redis): Redis client instance.
        client_id (str): Client identifier.
        limit (int): Max allowed requests per window.
        window_seconds (int): Time window in seconds."""
    key = build_rate_limit_key(client_id=client_id)

    current_value = redis_client.incr(key)
    if current_value == 1:
        redis_client.expire(key, window_seconds)

    allowed = current_value <= limit
    ttl_seconds = redis_client.ttl(key)

    return {
        'allowed': allowed,
        'current': current_value,
        'limit': limit,
        'ttl_seconds': ttl_seconds,
    }


def run_rate_limit_demo(
    client_id: str,
    limit: int,
    window_seconds: int,
    attempts: int,
    sleep_seconds: float,
) -> list[dict[str, Any]]:
    """Run rate limit demo with repeated requests.
    Args:
        client_id (str): Client identifier.
        limit (int): Max allowed requests per window.
        window_seconds (int): Time window in seconds.
        attempts (int): Number of simulated requests.
        sleep_seconds (float): Sleep between attempts."""
    redis_client = build_redis_client()
    results: list[dict[str, Any]] = []

    for _ in range(attempts):
        result = check_rate_limit(
            redis_client=redis_client,
            client_id=client_id,
            limit=limit,
            window_seconds=window_seconds,
        )
        results.append(result)
        time.sleep(sleep_seconds)

    return results


if __name__ == '__main__':
    demo_results = run_rate_limit_demo(
        client_id='client-1',
        limit=3,
        window_seconds=10,
        attempts=5,
        sleep_seconds=0.5,
    )
    print(demo_results)
