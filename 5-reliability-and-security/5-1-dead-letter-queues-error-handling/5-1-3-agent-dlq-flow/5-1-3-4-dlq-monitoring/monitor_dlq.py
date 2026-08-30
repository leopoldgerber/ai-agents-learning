import json
import logging
from typing import Any

import pika


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEAD_LETTER_QUEUE = 'dlq_queue'


def open_connection() -> pika.BlockingConnection:
    """Open a RabbitMQ connection.
    Args:
        None: No arguments."""
    connection_params = pika.ConnectionParameters(
        host='localhost',
    )

    return pika.BlockingConnection(connection_params)


def read_dlq_task(
    body: bytes,
) -> dict[str, Any]:
    """Deserialize one dead-lettered task.
    Args:
        body (bytes): Serialized task body."""
    task = json.loads(
        body.decode('utf-8'),
    )

    return task


def log_dlq_task(
    task: dict[str, Any],
) -> dict[str, Any]:
    """Log diagnostic data for a failed task.
    Args:
        task (dict[str, Any]): Dead-lettered task data."""
    logger.warning(
        'DLQ task: id=%s, type=%s, attempts=%s, payload=%s',
        task.get('task_id'),
        task.get('task_type'),
        task.get('attempts'),
        task.get('payload'),
    )

    return task


def handle_dlq_message(
    channel: Any,
    method: Any,
    properties: Any,
    body: bytes,
) -> dict[str, Any]:
    """Inspect and acknowledge one DLQ message.
    Args:
        channel (Any): RabbitMQ channel.
        method (Any): Delivery metadata.
        properties (Any): Message properties.
        body (bytes): Serialized task body."""
    del properties

    task = read_dlq_task(
        body=body,
    )
    logged_task = log_dlq_task(
        task=task,
    )

    channel.basic_ack(
        delivery_tag=method.delivery_tag,
    )

    return logged_task


def monitor_dlq() -> str:
    """Start consuming dead-lettered tasks.
    Args:
        None: No arguments."""
    connection = open_connection()
    channel = connection.channel()

    channel.basic_consume(
        queue=DEAD_LETTER_QUEUE,
        on_message_callback=handle_dlq_message,
        auto_ack=False,
    )

    logger.info('Monitoring %s', DEAD_LETTER_QUEUE)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()

    return 'monitor_stopped'


if __name__ == '__main__':
    monitor_status = monitor_dlq()
