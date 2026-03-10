import hashlib
import hmac
import json

import requests


def build_signature(body: bytes, secret_key: str) -> str:
    """Build HMAC signature for request body.
    Args:
        body (bytes): Raw request body.
        secret_key (str): Shared secret key."""
    digest = hmac.new(
        secret_key.encode('utf-8'),
        body,
        hashlib.sha256,
    ).hexdigest()
    return digest


def send_webhook(url: str, event: dict, secret_key: str) -> requests.Response:
    """Send webhook request to server.
    Args:
        url (str): Webhook endpoint URL.
        event (dict): Event payload.
        secret_key (str): Shared secret key."""
    body = json.dumps(event).encode('utf-8')
    signature = build_signature(body=body, secret_key=secret_key)
    headers = {
        'Content-Type': 'application/json',
        'X-Signature': signature,
    }
    response = requests.post(url, data=body, headers=headers, timeout=10)
    return response


def print_result(response: requests.Response) -> requests.Response:
    """Print response data.
    Args:
        response (requests.Response): HTTP response object."""
    print(f'Status code: {response.status_code}')
    print(f'Response body: {response.text}')
    return response


if __name__ == '__main__':
    webhook_url = 'http://127.0.0.1:8000/crm/webhook'
    secret_key = 'my-secret-key'
    event_data = {
        'id': 'lead-1001',
        'type': 'lead.created',
        'payload': {
            'name': 'Alice',
            'email': 'alice@example.com',
        },
    }

    response_data = send_webhook(
        url=webhook_url,
        event=event_data,
        secret_key=secret_key,
    )
    print_result(response=response_data)
