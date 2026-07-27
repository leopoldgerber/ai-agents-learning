import pika


MAIN_QUEUE = 'main_queue'
DEAD_LETTER_QUEUE = 'dlq_queue'


def open_connection() -> pika.BlockingConnection:
    """Open a RabbitMQ connection.
    Args:
        None: No arguments."""
    connection_params = pika.ConnectionParameters(
        host='localhost',
    )

    return pika.BlockingConnection(connection_params)


def setup_queues() -> dict[str, str]:
    """Declare queues with automatic dead-letter routing.
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

    return {
        'main_queue': MAIN_QUEUE,
        'dead_letter_queue': DEAD_LETTER_QUEUE,
    }


if __name__ == '__main__':
    declared_queues = setup_queues()
    print(f'Declared queues: {declared_queues}')
