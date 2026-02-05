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


def build_queue_name() -> str:
    """Build Redis list key used as a tasks queue.
    Args:
        None: No arguments."""
    return 'tasks_queue'


def decode_task(raw_task: bytes) -> dict[str, Any]:
    """Decode a task payload from Redis into dict.
    Args:
        raw_task (bytes): Raw bytes from Redis list."""
    text_value = raw_task.decode('utf-8')
    return json.loads(text_value)


def pop_task_blocking(
        redis_client: redis.Redis,
        queue_name: str,
        timeout_seconds: int
) -> dict[str, Any]:
    """Pop one task from Redis list using BLPOP.
    Args:
        redis_client (redis.Redis): Redis client instance.
        queue_name (str): Redis list key.
        timeout_seconds (int): Blocking pop timeout in seconds."""
    result = redis_client.blpop(queue_name, timeout=timeout_seconds)
    if result is None:
        return {'found': False}

    _, raw_task = result
    return {'found': True, 'task': decode_task(raw_task=raw_task)}


def process_task(task_data: dict[str, Any]) -> dict[str, Any]:
    """Simulate task processing.
    Args:
        task_data (dict[str, Any]): Decoded task data."""
    time.sleep(0.1)
    return {
        'processed': True,
        'task_id': task_data.get('task_id'),
        'task_type': task_data.get('task_type')
    }


def run_worker_demo(max_tasks: int, timeout_seconds: int) -> dict[str, Any]:
    """Run worker demo: consume up to N tasks using blocking pop.
    Args:
        max_tasks (int): Max number of tasks to process.
        timeout_seconds (int): BLPOP timeout in seconds."""
    redis_client = build_redis_client()
    queue_name = build_queue_name()

    processed_list: list[dict[str, Any]] = []
    for _ in range(max_tasks):
        popped = pop_task_blocking(
            redis_client=redis_client,
            queue_name=queue_name,
            timeout_seconds=timeout_seconds,
        )
        if not popped.get('found'):
            break

        processed_list.append(process_task(task_data=popped['task']))

    return {
        'queue': queue_name,
        'processed': processed_list,
        'count': len(processed_list)
    }


if __name__ == '__main__':
    worker_result = run_worker_demo(max_tasks=5, timeout_seconds=2)
    print(worker_result)
