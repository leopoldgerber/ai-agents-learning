import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, TypedDict

import pika


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_QUEUE = 'main_queue'
POISON_QUEUE = 'poison_messages'
MAX_RETRIES = 3

failure_counts: dict[str, int] = {}


class AlertData(TypedDict):
    """Store poison message alert data."""

    timestamp: str
    message_id: str
    error: str
    body_preview: str
    attempts: int
    severity: str


def open_connection() -> pika.BlockingConnection:
    """Open a RabbitMQ connection.
    Args:
        None: No arguments."""
    connection_params = pika.ConnectionParameters(
        host='localhost',
    )

    return pika.BlockingConnection(connection_params)


def declare_queues() -> list[str]:
    """Declare main and poison message queues.
    Args:
        None: No arguments."""
    connection = open_connection()
    channel = connection.channel()

    channel.queue_declare(
        queue=MAIN_QUEUE,
        durable=True,
    )
    channel.queue_declare(
        queue=POISON_QUEUE,
        durable=True,
    )

    connection.close()

    return [MAIN_QUEUE, POISON_QUEUE]


def extract_message_id(body: bytes) -> str:
    """Extract a stable message identifier.
    Args:
        body (bytes): Serialized message body."""
    try:
        message = json.loads(body.decode('utf-8'))
        message_id = str(message.get('message_id', '')).strip()

        if message_id:
            return message_id

    except (json.JSONDecodeError, UnicodeDecodeError):
        pass

    body_hash = hashlib.sha256(body).hexdigest()

    return body_hash[:16]


def validate_message(
    data: dict[str, Any],
) -> tuple[bool, str]:
    """Validate message structure and business fields.
    Args:
        data (dict[str, Any]): Deserialized message data."""
    required_fields = [
        'message_id',
        'user_id',
        'action',
        'payload',
    ]

    for field_name in required_fields:
        if field_name not in data:
            return False, f'Missing required field: {field_name}'

    if not isinstance(data['user_id'], (int, str)):
        return False, 'Field user_id must be an integer or string'

    if not isinstance(data['payload'], dict):
        return False, 'Field payload must be an object'

    allowed_actions = {
        'create',
        'update',
        'delete',
    }

    if data['action'] not in allowed_actions:
        return False, f"Unsupported action: {data['action']}"

    return True, ''


def process_message(
    body: bytes,
) -> tuple[bool, str]:
    """Process one message with validation.
    Args:
        body (bytes): Serialized message body."""
    try:
        message = json.loads(body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        return False, f'JSON parsing error: {error}'

    is_valid, validation_error = validate_message(
        data=message,
    )

    if not is_valid:
        return False, f'Validation error: {validation_error}'

    message_id = str(message['message_id'])
    logger.info('Processing message %s', message_id)

    return True, ''


def record_failure(
    message_id: str,
) -> int:
    """Record one failed processing attempt.
    Args:
        message_id (str): Unique message identifier."""
    failure_counts[message_id] = (
        failure_counts.get(message_id, 0) + 1
    )

    return failure_counts[message_id]


def reset_failure(
    message_id: str,
) -> int:
    """Reset the failure counter after success.
    Args:
        message_id (str): Unique message identifier."""
    failure_counts.pop(message_id, None)

    return 0


def build_alert(
    message_id: str,
    body: bytes,
    error: str,
    attempts: int,
) -> AlertData:
    """Build structured poison message alert data.
    Args:
        message_id (str): Unique message identifier.
        body (bytes): Serialized message body.
        error (str): Processing error description.
        attempts (int): Number of failed attempts."""
    severity = 'critical' if 'validation' in error.lower() else 'warning'

    return {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'message_id': message_id,
        'error': error,
        'body_preview': body[:200].decode(
            'utf-8',
            errors='ignore',
        ),
        'attempts': attempts,
        'severity': severity,
    }


def send_alert(
    alert_data: AlertData,
) -> AlertData:
    """Send a structured alert through logging.
    Args:
        alert_data (AlertData): Poison message alert data."""
    alert_text = json.dumps(
        alert_data,
        ensure_ascii=False,
    )
    logger.error('POISON MESSAGE ALERT: %s', alert_text)

    return alert_data


def publish_poison(
    channel: Any,
    alert_data: AlertData,
) -> AlertData:
    """Publish poison message data to its queue.
    Args:
        channel (Any): RabbitMQ channel.
        alert_data (AlertData): Poison message metadata."""
    message_body = json.dumps(
        alert_data,
        ensure_ascii=False,
    )

    channel.basic_publish(
        exchange='',
        routing_key=POISON_QUEUE,
        body=message_body,
        properties=pika.BasicProperties(
            content_type='application/json',
            delivery_mode=2,
            headers={
                'poison_reason': alert_data['error'],
                'attempts': alert_data['attempts'],
            },
        ),
    )

    return alert_data


def handle_message(
    channel: Any,
    method: Any,
    properties: Any,
    body: bytes,
) -> dict[str, Any]:
    """Handle one delivery with poison message protection.
    Args:
        channel (Any): RabbitMQ channel.
        method (Any): Message delivery metadata.
        properties (Any): RabbitMQ message properties.
        body (bytes): Serialized message body."""
    del properties

    message_id = extract_message_id(body=body)
    is_successful, processing_error = process_message(
        body=body,
    )

    if is_successful:
        reset_failure(message_id=message_id)
        channel.basic_ack(
            delivery_tag=method.delivery_tag,
        )
        logger.info('Message %s processed', message_id)

        return {
            'message_id': message_id,
            'status': 'processed',
            'attempts': 0,
        }

    attempts = record_failure(
        message_id=message_id,
    )

    if attempts < MAX_RETRIES:
        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=True,
        )
        logger.warning(
            'Message %s returned to queue: %s/%s',
            message_id,
            attempts,
            MAX_RETRIES,
        )

        return {
            'message_id': message_id,
            'status': 'retrying',
            'attempts': attempts,
        }

    alert_data = build_alert(
        message_id=message_id,
        body=body,
        error=processing_error,
        attempts=attempts,
    )
    sent_alert = send_alert(
        alert_data=alert_data,
    )
    published_alert = publish_poison(
        channel=channel,
        alert_data=sent_alert,
    )

    channel.basic_ack(
        delivery_tag=method.delivery_tag,
    )
    reset_failure(
        message_id=message_id,
    )

    return {
        'message_id': message_id,
        'status': 'poisoned',
        'attempts': published_alert['attempts'],
    }


def start_consumer() -> str:
    """Start the poison-aware message consumer.
    Args:
        None: No arguments."""
    connection = open_connection()
    channel = connection.channel()

    channel.basic_qos(
        prefetch_count=1,
    )
    channel.basic_consume(
        queue=MAIN_QUEUE,
        on_message_callback=handle_message,
        auto_ack=False,
    )

    logger.info('Waiting for messages in %s', MAIN_QUEUE)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        connection.close()

    return 'consumer_stopped'


if __name__ == '__main__':
    declared_queues = declare_queues()
    consumer_status = start_consumer()
