import requests
import hmac
import hashlib
import json

API_URL = "https://your-agent.com/webhook"
CRM_API = "https://crm.example.com/api/leads"
SECRET = "webhook_secret"


def test_webhook_creates_lead_in_crm():
    """E2E test: webhook arrives, agent creates a lead in CRM"""

    # 1. Prepare webhook data
    webhook_data = {
        "event_id": "test-event-123",
        "event": "form_submitted",
        "lead": {
            "name": "Иван Тестов",
            "email": "ivan@test.com",
            "phone": "+7 999 000-00-00"
        }
    }

    payload = json.dumps(webhook_data)

    # 2. Compute request signature
    signature = hmac.new(
        SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    # 3. Send webhook to our server
    response = requests.post(
        API_URL,
        data=payload,
        headers={
            "X-Webhook-Signature": signature,
            "Content-Type": "application/json"
        }
    )

    # 4. Verify that webhook was accepted
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # 5. Verify that the lead was actually created in CRM
    # (In real scenarios authorization is required here)
    crm_response = requests.get(
        f"{CRM_API}?email=ivan@test.com",
        headers={"Authorization": "Bearer test_token"}
    )

    assert crm_response.status_code == 200
    leads = crm_response.json()
    assert len(leads) > 0
    assert leads[0]["email"] == "ivan@test.com"
    assert leads[0]["name"] == "Ivan Test"
