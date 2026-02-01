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


# === extra added to control Redis events
def list_active_events(redis_client: Redis) -> list[dict[str, str]]:
    """List active deduplicated events stored in Redis.
    Args:
        redis_client (Redis): Redis client instance."""
    keys = redis_client.keys('webhook:event:*')
    active_events: list[dict[str, str]] = []

    for key in keys:
        ttl_s = redis_client.ttl(key)
        event_id = key.replace('webhook:event:', '', 1)
        active_events.append(
            {
                'event_id': event_id,
                'ttl_seconds': str(ttl_s),
            }
        )
    return active_events


def delete_event(redis_client: Redis, event_id: str) -> bool:
    """Delete a deduplicated event from Redis by event id.
    Args:
        redis_client (Redis): Redis client instance.
        event_id (str): Unique event identifier."""
    event_key = build_event_key(event_id=event_id)
    deleted_count = redis_client.delete(event_key)
    return deleted_count == 1


if __name__ == '__main__':
    redis_client = build_redis_client(host='localhost', port=6379, db=0)

    result_1 = handle_event(
        redis_client=redis_client,
        event_id='evt_1',
        payload={'type': 'invoice.paid'},
        ttl_s=30,
    )
    result_2 = handle_event(
        redis_client=redis_client,
        event_id='evt_1',
        payload={'type': 'invoice.paid'},
        ttl_s=30,
    )

    print(f'result_1 [evt_1]: {result_1}')
    print(f'result_2 [evt_1]: {result_2}')

    # Check Redis active events
    result = list_active_events(redis_client)

    result_3 = handle_event(
        redis_client=redis_client,
        event_id='evt_2',
        payload={'type': 'invoice.paid'},
        ttl_s=30,
    )

    print(f'\nRedis list: {result}')

    # Redis delete evt_1 and evt_2
    delete_event(event_id='evt_1', redis_client=redis_client)
    delete_event(event_id='evt_2', redis_client=redis_client)

    print(f'result_3 [evt_2]: {result_3}')
