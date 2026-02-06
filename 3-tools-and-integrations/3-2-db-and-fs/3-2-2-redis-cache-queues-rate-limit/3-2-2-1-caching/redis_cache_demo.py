import json
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


def build_cache_key(user_id: int) -> str:
    """Build cache key for user profile.
    Args:
        user_id (int): User identifier."""
    return f'user:{user_id}:profile'


def fetch_user_profile(user_id: int) -> dict[str, Any]:
    """Simulate slow database/API fetch for user profile.
    Args:
        user_id (int): User identifier."""
    time.sleep(0.2)
    return {'user_id': user_id, 'name': 'Alex', 'role': 'member'}


def read_cached_profile(
        redis_client: redis.Redis,
        cache_key: str
) -> dict[str, Any]:
    """Read cached JSON profile by key.
    Args:
        redis_client (redis.Redis): Redis client instance.
        cache_key (str): Cache key."""
    raw_value = redis_client.get(cache_key)
    if raw_value is None:
        return {'hit': False}

    return {'hit': True, 'profile': json.loads(raw_value.decode('utf-8'))}


def write_cached_profile(
    redis_client: redis.Redis,
    cache_key: str,
    profile: dict[str, Any],
    ttl_seconds: int,
) -> bool:
    """Write JSON profile to Redis with TTL.
    Args:
        redis_client (redis.Redis): Redis client instance.
        cache_key (str): Cache key.
        profile (dict[str, Any]): Profile payload.
        ttl_seconds (int): Key time-to-live in seconds."""
    payload = json.dumps(profile, ensure_ascii=False)
    return bool(redis_client.set(cache_key, payload, ex=ttl_seconds))


def get_profile_cache_aside(
    redis_client: redis.Redis,
    user_id: int,
    ttl_seconds: int,
) -> dict[str, Any]:
    """Get user profile using cache-aside pattern.
    Args:
        redis_client (redis.Redis): Redis client instance.
        user_id (int): User identifier.
        ttl_seconds (int): Key time-to-live in seconds."""
    cache_key = build_cache_key(user_id=user_id)
    cached = read_cached_profile(
        redis_client=redis_client,
        cache_key=cache_key
    )
    if cached.get('hit'):
        return {'source': 'cache', 'data': cached['profile']}

    profile = fetch_user_profile(user_id=user_id)
    write_cached_profile(
        redis_client=redis_client,
        cache_key=cache_key,
        profile=profile,
        ttl_seconds=ttl_seconds,
    )
    return {'source': 'db', 'data': profile}


def run_cache_demo(ttl_seconds: int) -> dict[str, Any]:
    """Run caching demo: first call miss, second call hit.
    Args:
        ttl_seconds (int): Key time-to-live in seconds."""
    redis_client = build_redis_client()
    user_id_value = 1

    first = get_profile_cache_aside(
        redis_client=redis_client,
        user_id=user_id_value,
        ttl_seconds=ttl_seconds,
    )
    second = get_profile_cache_aside(
        redis_client=redis_client,
        user_id=user_id_value,
        ttl_seconds=ttl_seconds,
    )

    return {'first_call': first, 'second_call': second}


if __name__ == '__main__':
    result_data = run_cache_demo(ttl_seconds=10)
    print(result_data)
