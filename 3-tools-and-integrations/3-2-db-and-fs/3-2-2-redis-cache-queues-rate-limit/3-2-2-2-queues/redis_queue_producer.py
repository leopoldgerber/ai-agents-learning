import json
import os
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


def build_task_payload(
        task_id: int,
        task_type: str,
        payload: dict[str, Any]
) -> str:
    """Build JSON payload for a queue task.
    Args:
        task_id (int): Task identifier.
        task_type (str): Task type name.
        payload (dict[str, Any]): Task payload data."""
    task_data = {
        'task_id': task_id,
        'task_type': task_type,
        'payload': payload
    }
    return json.dumps(task_data, ensure_ascii=False)


def enqueue_tasks(
        redis_client: redis.Redis,
        queue_name: str,
        tasks_list: list[str]
) -> int:
    """Push tasks to Redis list using RPUSH.
    Args:
        redis_client (redis.Redis): Redis client instance.
        queue_name (str): Redis list key.
        tasks_list (list[str]): Task payloads to enqueue."""
    if not tasks_list:
        return 0

    return int(redis_client.rpush(queue_name, *tasks_list))


def run_producer_demo(tasks_count: int) -> dict[str, Any]:
    """Run producer demo: enqueue several tasks into Redis list.
    Args:
        tasks_count (int): Number of tasks to enqueue."""
    redis_client = build_redis_client()
    queue_name = build_queue_name()

    tasks_list: list[str] = []
    for task_id in range(1, tasks_count + 1):
        task_payload = build_task_payload(
            task_id=task_id,
            task_type='send_email',
            payload={'to': 'alex@example.com', 'template': 'welcome'},
        )
        tasks_list.append(task_payload)

    new_length = enqueue_tasks(
        redis_client=redis_client,
        queue_name=queue_name,
        tasks_list=tasks_list
    )
    return {
        'queue': queue_name,
        'enqueued': len(tasks_list),
        'queue_length': new_length
    }


if __name__ == '__main__':
    producer_result = run_producer_demo(tasks_count=3)
    print(producer_result)
