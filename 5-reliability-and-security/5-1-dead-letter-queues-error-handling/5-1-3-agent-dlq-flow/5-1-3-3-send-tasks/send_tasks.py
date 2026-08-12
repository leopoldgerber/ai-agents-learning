import json
import uuid
from datetime import datetime, timezone
from typing import Any

import pika


MAIN_QUEUE = 'main_queue'


def open_connection() -> pika.BlockingConnection:
    """Open a RabbitMQ connection.
    Args:
        None: No arguments."""
    connection_params = pika.ConnectionParameters(
        host='localhost',
    )

    return pika.BlockingConnection(connection_params)


def build_task(
    task_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Build a new agent task.
    Args:
        task_type (str): Task handler type.
        payload (dict[str, Any]): Task-specific input data."""
    task = {
        'task_id': str(uuid.uuid4()),
        'task_type': task_type,
        'payload': payload,
        'created_at': datetime.now(
            timezone.utc,
        ).isoformat(),
        'attempts': 0,
    }

    return task


def publish_task(
    channel: Any,
    task: dict[str, Any],
) -> dict[str, Any]:
    """Publish one task to the main queue.
    Args:
        channel (Any): RabbitMQ channel.
        task (dict[str, Any]): Structured agent task."""
    message_body = json.dumps(
        task,
        ensure_ascii=False,
    )

    channel.basic_publish(
        exchange='',
        routing_key=MAIN_QUEUE,
        body=message_body,
        properties=pika.BasicProperties(
            content_type='application/json',
            delivery_mode=2,
        ),
    )

    return task


def send_task(
    task_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Build and send one agent task.
    Args:
        task_type (str): Task handler type.
        payload (dict[str, Any]): Task-specific input data."""
    connection = open_connection()
    channel = connection.channel()

    task = build_task(
        task_type=task_type,
        payload=payload,
    )
    published_task = publish_task(
        channel=channel,
        task=task,
    )

    connection.close()

    return published_task


if __name__ == '__main__':
    email_task = send_task(
        task_type='send_email',
        payload={
            'to': 'user@example.com',
            'subject': 'Welcome!',
            'body': 'Hello!',
        },
    )
    invalid_email_task = send_task(
        task_type='send_email',
        payload={
            'to': 'user@example.com',
        },
    )

    print(f"Published task: {email_task['task_id']}")
    print(
        f"Published invalid task: "
        f"{invalid_email_task['task_id']}"
    )
