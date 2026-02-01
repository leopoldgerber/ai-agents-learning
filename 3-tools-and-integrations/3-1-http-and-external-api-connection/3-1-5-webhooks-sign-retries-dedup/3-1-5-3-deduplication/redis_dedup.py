from typing import Any
from redis import Redis
# import redis.asyncio as redis


def build_redis_client(host: str, port: int, db: int) -> Redis:
    """Build a Redis client.
    Args:
        host (str): Redis host.
        port (int): Redis port.
        db (int): Redis database index."""
    return Redis(host=host, port=port, db=db, decode_responses=True)


def build_event_key(event_id: str) -> str:
    """Build a Redis key for an event id.
    Args:
        event_id (str): Unique event identifier."""
    return f'webhook:event:{event_id}'


def mark_event_received(
        redis_client: Redis, event_id: str, ttl_s: int) -> bool:
    """Try to mark event as received using NX + TTL.
    Args:
        redis_client (Redis): Redis client instance.
        event_id (str): Unique event identifier.
        ttl_s (int): Time-to-live in seconds."""
    event_key = build_event_key(event_id=event_id)
    return bool(redis_client.set(name=event_key, value='1', ex=ttl_s, nx=True))


def handle_event(
        redis_client: Redis,
        event_id: str,
        payload: dict[str, Any],
        ttl_s: int
) -> str:
    """Handle incoming event with Redis-based deduplication.
    Args:
        redis_client (Redis): Redis client instance.
        event_id (str): Unique event identifier.
        payload (dict[str, Any]): Event payload.
        ttl_s (int): Time-to-live in seconds."""
    is_first_delivery = mark_event_received(
        redis_client=redis_client, event_id=event_id, ttl_s=ttl_s)
    if not is_first_delivery:
        return 'duplicate'

    _ = payload
    return 'processed'


if __name__ == '__main__':
    redis_client = build_redis_client(host='localhost', port=6379, db=0)

    result_1 = handle_event(
        redis_client=redis_client,
        event_id='evt_1',
        payload={'type': 'invoice.paid'},
        ttl_s=3600,
    )
    result_2 = handle_event(
        redis_client=redis_client,
        event_id='evt_1',
        payload={'type': 'invoice.paid'},
        ttl_s=3600,
    )

    print(result_1)
    print(result_2)
