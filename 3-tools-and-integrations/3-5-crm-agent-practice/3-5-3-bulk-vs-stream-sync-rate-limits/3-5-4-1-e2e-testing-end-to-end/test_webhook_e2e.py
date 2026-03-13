import json
import hmac
import hashlib
import requests


API_URL = 'https://your-agent.com/webhook'
CRM_API = 'https://crm.example.com/api/leads'
SECRET = 'webhook_secret'


def build_signature(payload: str) -> str:
    """Build webhook signature.
    Args:
        payload (str): JSON payload string."""
    return hmac.new(
        SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()


def send_webhook(payload: str, signature: str) -> requests.Response:
    """Send webhook to agent.
    Args:
        payload (str): JSON payload string.
        signature (str): HMAC signature."""
    return requests.post(
        API_URL,
        data=payload,
        headers={
            'X-Webhook-Signature': signature,
            'Content-Type': 'application/json'
        }
    )


def check_lead_in_crm(email: str) -> dict:
    """Check that lead exists in CRM.
    Args:
        email (str): Lead email."""
    response = requests.get(
        f'{CRM_API}?email={email}',
        headers={'Authorization': 'Bearer test_token'}
    )

    response.raise_for_status()
    return response.json()


def test_webhook_creates_lead():
    """End-to-end test for webhook → CRM lead creation."""
    webhook_data = {
        'event_id': 'test-event-123',
        'event': 'form_submitted',
        'lead': {
            'name': 'Ivan Test',
            'email': 'ivan@test.com',
            'phone': '+7 999 000-00-00'
        }
    }

    payload = json.dumps(webhook_data)
    signature = build_signature(payload)

    response = send_webhook(payload, signature)

    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

    leads = check_lead_in_crm('ivan@test.com')

    assert len(leads) > 0
    assert leads[0]['email'] == 'ivan@test.com'
