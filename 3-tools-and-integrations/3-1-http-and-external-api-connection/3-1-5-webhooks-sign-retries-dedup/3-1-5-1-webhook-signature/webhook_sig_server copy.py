import hashlib
import hmac
import json
from typing import Any

from fastapi import FastAPI, HTTPException, Request


app = FastAPI()

WEBHOOK_SECRET = b'super_secret_key'
SIGNATURE_HEADER = 'X-Signature'


def build_hmac_hex(secret: bytes, raw_body: bytes) -> str:
    """Build HMAC-SHA256 hex digest for raw request body.
    Args:
        secret (bytes): Shared webhook secret.
        raw_body (bytes): Raw HTTP request body bytes."""
    digest = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    return digest


def read_signature(headers: dict[str, str]) -> str:
    headers_lc = {k.lower(): v for k, v in headers.items()}
    return headers_lc.get(SIGNATURE_HEADER.lower(), '').strip()


def verify_signature(secret: bytes, raw_body: bytes, signature: str) -> None:
    """Verify webhook signature using constant-time comparison.
    Args:
        secret (bytes): Shared webhook secret.
        raw_body (bytes): Raw HTTP request body bytes.
        signature (str): Signature header value."""
    if signature == '':
        raise HTTPException(status_code=400, detail='Missing signature header')

    expected = build_hmac_hex(secret=secret, raw_body=raw_body)
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail='Invalid signature')


def parse_json(raw_body: bytes) -> dict[str, Any]:
    """Parse JSON payload from raw body bytes.
    Args:
        raw_body (bytes): Raw HTTP request body bytes."""
    try:
        payload = json.loads(raw_body.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=400, detail='Invalid JSON body') from exc

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=400, detail='JSON payload must be an object')

    return payload


@app.get('/health')
async def health() -> dict[str, bool]:
    """Health check endpoint.
    Args:
        None: No arguments."""
    return {'ok': True}


@app.post('/webhook')
async def webhook(request: Request) -> dict[str, Any]:
    """Webhook endpoint with signature verification.
    Args:
        request (Request): FastAPI request object."""
    raw_body = await request.body()
    signature = read_signature(headers=dict(request.headers))

    verify_signature(
        secret=WEBHOOK_SECRET, raw_body=raw_body, signature=signature)
    payload = parse_json(raw_body=raw_body)

    event_type = str(payload.get('type', 'unknown'))
    event_id = str(payload.get('id', 'missing'))

    return {'ok': True, 'event_type': event_type, 'event_id': event_id}
