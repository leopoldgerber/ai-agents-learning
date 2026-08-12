import json
import logging
from typing import Any

import pika


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_QUEUE = 'main_queue'


def open_connection() -> pika.BlockingConnection:
    """Open a RabbitMQ connection.
    Args:
        None: No arguments."""
    connection_params = pika.ConnectionParameters(
        host='localhost',
    )

    return pika.BlockingConnection(connection_params)


def read_task(
    body: bytes,
) -> dict[str, Any]:
    """Deserialize and validate a task envelope.
    Args:
        body (bytes): Serialized task body."""
    try:
        task = json.loads(
            body.decode('utf-8'),
        )
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError(
            f'Invalid task JSON: {error}'
        ) from error

    if not isinstance(task, dict):
        raise ValueError('Task body must be an object')

    return task


class TaskProcessor:
    """Process agent tasks with retry and DLQ support."""

    def __init__(
        self,
        max_retries: int = 3,
    ) -> None:
        self.max_retries = max_retries
        self.connection = open_connection()
        self.channel = self.connection.channel()
        self.channel.basic_qos(
            prefetch_count=1,
        )

    def handle_email(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle one email task.
        Args:
            payload (dict[str, Any]): Email task payload."""
        required_fields = {
            'to',
            'subject',
        }
        missing_fields = required_fields - payload.keys()

        if missing_fields:
            missing_text = ', '.join(
                sorted(missing_fields),
            )
            raise ValueError(
                f'Missing email fields: {missing_text}'
            )

        logger.info(
            'Sending email to %s',
            payload['to'],
        )

        return payload

    def handle_order(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Handle one order task.
        Args:
            payload (dict[str, Any]): Order task payload."""
        if 'order_id' not in payload:
            raise ValueError('Missing order_id')

        logger.info(
            'Processing order %s',
            payload['order_id'],
        )

        return payload

    def dispatch_task(
        self,
        task: dict[str, Any],
    ) -> dict[str, Any]:
        """Dispatch a task to its matching handler.
        Args:
            task (dict[str, Any]): Deserialized task data."""
        task_type = str(
            task.get('task_type', ''),
        )
        payload = task.get('payload', {})

        if not isinstance(payload, dict):
            raise ValueError('Task payload must be an object')

        if task_type == 'send_email':
            return self.handle_email(
                payload=payload,
            )

        if task_type == 'process_order':
            return self.handle_order(
                payload=payload,
            )

        raise ValueError(
            f'Unsupported task type: {task_type}'
        )

    def publish_retry(
        self,
        task: dict[str, Any],
    ) -> dict[str, Any]:
        """Republish a task with an updated attempt count.
        Args:
            task (dict[str, Any]): Failed task data."""
        message_body = json.dumps(
            task,
            ensure_ascii=False,
        )

        self.channel.basic_publish(
            exchange='',
            routing_key=MAIN_QUEUE,
            body=message_body,
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2,
            ),
        )

        return task

    def process_message(
        self,
        channel: Any,
        method: Any,
        properties: Any,
        body: bytes,
    ) -> dict[str, Any]:
        """Process one delivered task message.
        Args:
            channel (Any): RabbitMQ channel.
            method (Any): Delivery metadata.
            properties (Any): Message properties.
            body (bytes): Serialized task body."""
        del properties

        try:
            task = read_task(
                body=body,
            )
        except ValueError as error:
            logger.error(
                'Task decoding failed: %s',
                error,
            )
            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )

            return {
                'task_id': 'unknown',
                'status': 'dead_lettered',
                'attempts': 0,
            }

        task_id = str(
            task.get('task_id', 'unknown'),
        )

        try:
            self.dispatch_task(
                task=task,
            )
            channel.basic_ack(
                delivery_tag=method.delivery_tag,
            )
            logger.info(
                'Task %s completed',
                task_id,
            )

            return {
                'task_id': task_id,
                'status': 'completed',
                'attempts': int(
                    task.get('attempts', 0),
                ),
            }

        except (KeyError, TypeError, ValueError) as error:
            attempts = int(
                task.get('attempts', 0),
            ) + 1
            task['attempts'] = attempts

            logger.error(
                'Task %s failed: %s',
                task_id,
                error,
            )

            if attempts < self.max_retries:
                self.publish_retry(
                    task=task,
                )
                channel.basic_ack(
                    delivery_tag=method.delivery_tag,
                )
                logger.warning(
                    'Task %s republished: %s/%s',
                    task_id,
                    attempts,
                    self.max_retries,
                )

                return {
                    'task_id': task_id,
                    'status': 'retrying',
                    'attempts': attempts,
                }

            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False,
            )
            logger.error(
                'Task %s sent to DLQ',
                task_id,
            )

            return {
                'task_id': task_id,
                'status': 'dead_lettered',
                'attempts': attempts,
            }

    def start_consumer(
        self,
    ) -> str:
        """Start consuming tasks from the main queue.
        Args:
            None: No arguments."""
        self.channel.basic_consume(
            queue=MAIN_QUEUE,
            on_message_callback=self.process_message,
            auto_ack=False,
        )

        logger.info(
            'Waiting for tasks in %s',
            MAIN_QUEUE,
        )

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        finally:
            self.connection.close()

        return 'consumer_stopped'


if __name__ == '__main__':
    task_processor = TaskProcessor(
        max_retries=3,
    )
    consumer_status = task_processor.start_consumer()
