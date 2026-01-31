import hashlib
import hmac
import json
from typing import Any

import requests


WEBHOOK_SECRET = b'super_secret_key'
SIGNATURE_HEADER = 'X-Signature'


def build_payload(event_id: str, event_type: str) -> dict[str, Any]:
    """Build a minimal webhook payload.
    Args:
        event_id (str): Event unique identifier.
        event_type (str): Event type name."""
    payload = {'id': event_id, 'type': event_type}
    return payload


def encode_body(payload: dict[str, Any]) -> bytes:
    """Encode payload as JSON bytes.
    Args:
        payload (dict[str, Any]): JSON-serializable payload."""
    raw_body = json.dumps(
        payload, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return raw_body


def build_hmac_hex(secret: bytes, raw_body: bytes) -> str:
    """Build HMAC-SHA256 hex digest for raw request body.
    Args:
        secret (bytes): Shared webhook secret.
        raw_body (bytes): Raw HTTP request body bytes."""
    digest = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    return digest


def send_webhook(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Send signed webhook request to server.
    Args:
        url (str): Webhook endpoint URL.
        payload (dict[str, Any]): Webhook payload."""
    raw_body = encode_body(payload=payload)
    signature = build_hmac_hex(secret=WEBHOOK_SECRET, raw_body=raw_body)

    headers = {
        'Content-Type': 'application/json',
        SIGNATURE_HEADER: signature,
    }

    response = requests.post(url, data=raw_body, headers=headers, timeout=15)
    response.raise_for_status()

    response_payload = response.json()
    if not isinstance(response_payload, dict):
        return {'raw': response.text}

    return response_payload


if __name__ == '__main__':
    webhook_url = 'http://localhost:8000/webhook'
    event_payload = build_payload(
        event_id='evt_123', event_type='invoice.paid')
    result = send_webhook(url=webhook_url, payload=event_payload)
    print(result)
