import hashlib
import hmac


SECRET_KEY = 'my-secret-key'
PROCESSED_EVENT_IDS: set[str] = set()


def build_signature(body: bytes, secret_key: str) -> str:
    """Build HMAC signature for raw request body.
    Args:
        body (bytes): Raw request body.
        secret_key (str): Shared secret key."""
    digest = hmac.new(
        secret_key.encode('utf-8'),
        body,
        hashlib.sha256,
    ).hexdigest()
    return digest


def verify_signature(body: bytes, signature: str | None) -> bool:
    """Verify request signature against shared secret.
    Args:
        body (bytes): Raw request body.
        signature (str | None): Signature from request headers."""
    if signature is None:
        return False

    expected_signature = build_signature(
        body=body,
        secret_key=SECRET_KEY,
    )
    is_valid = hmac.compare_digest(expected_signature, signature)
    return is_valid


def is_duplicate_event(event_id: str) -> bool:
    """Check whether event id was already processed.
    Args:
        event_id (str): Unique event identifier."""
    if not event_id:
        return False

    if event_id in PROCESSED_EVENT_IDS:
        return True

    PROCESSED_EVENT_IDS.add(event_id)
    return False
