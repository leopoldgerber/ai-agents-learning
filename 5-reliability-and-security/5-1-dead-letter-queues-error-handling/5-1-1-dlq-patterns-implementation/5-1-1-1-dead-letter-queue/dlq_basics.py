import json
from typing import Any

import pika


MAIN_QUEUE = 'tasks.main'
DEAD_LETTER_QUEUE = 'tasks.dlq'


def open_connection() -> pika.BlockingConnection:
    """Open a RabbitMQ connection.
    Args:
        None: No arguments."""
    connection_params = pika.ConnectionParameters(
        host='localhost',
    )

    return pika.BlockingConnection(connection_params)


def setup_queues() -> list[str]:
    """Declare the main queue and dead-letter queue.
    Args:
        None: No arguments."""
    connection = open_connection()
    channel = connection.channel()

    channel.queue_declare(
        queue=DEAD_LETTER_QUEUE,
        durable=True,
    )
    channel.queue_declare(
        queue=MAIN_QUEUE,
        durable=True,
        arguments={
            'x-dead-letter-exchange': '',
            'x-dead-letter-routing-key': DEAD_LETTER_QUEUE,
        },
    )

    connection.close()

    return [MAIN_QUEUE, DEAD_LETTER_QUEUE]


def publish_messages() -> list[dict[str, Any]]:
    """Publish successful and failing demo messages.
    Args:
        None: No arguments."""
    connection = open_connection()
    channel = connection.channel()

    messages = [
        {
            'id': 'task-1',
            'fail': False,
        },
        {
            'id': 'task-2',
            'fail': True,
        },
    ]

    for message in messages:
        message_body = json.dumps(message)

        channel.basic_publish(
            exchange='',
            routing_key=MAIN_QUEUE,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )

    connection.close()

    return messages


def process_message(
    channel: Any,
    method: Any,
    properties: Any,
    body: bytes,
) -> dict[str, str]:
    """Process one message from the main queue.
    Args:
        channel (Any): RabbitMQ channel.
        method (Any): Message delivery metadata.
        properties (Any): RabbitMQ message properties.
        body (bytes): Serialized message body."""
    del properties

    try:
        message = json.loads(body.decode('utf-8'))

        if message.get('fail'):
            raise ValueError('Demonstration processing error')

        channel.basic_ack(
            delivery_tag=method.delivery_tag,
        )
        print(f"Processed message: {message['id']}")

        return {
            'message_id': str(message['id']),
            'status': 'processed',
        }

    except (json.JSONDecodeError, KeyError, ValueError) as error:
        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False,
        )
        print(f'Failed message moved to DLQ: {error}')

        return {
            'message_id': 'unknown',
            'status': 'dead-lettered',
        }


def start_consumer() -> str:
    """Start consuming messages from the main queue.
    Args:
        None: No arguments."""
    connection = open_connection()
    channel = connection.channel()

    channel.basic_qos(
        prefetch_count=1,
    )
    channel.basic_consume(
        queue=MAIN_QUEUE,
        on_message_callback=process_message,
    )

    print(f'Waiting for messages in {MAIN_QUEUE}')
    channel.start_consuming()

    connection.close()

    return 'consumer_stopped'


if __name__ == '__main__':
    declared_queues = setup_queues()
    published_messages = publish_messages()
    consumer_status = start_consumer()
