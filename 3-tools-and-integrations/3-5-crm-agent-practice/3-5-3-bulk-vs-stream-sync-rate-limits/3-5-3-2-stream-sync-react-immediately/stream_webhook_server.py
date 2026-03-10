from typing import Any
from fastapi import FastAPI, Request


app = FastAPI()


def parse_event(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract event information from webhook payload.
    Args:
        payload (dict[str, Any]): Webhook request payload."""
    event_type = payload.get('event')
    data = payload.get('data', {})

    return {
        'event': event_type,
        'lead_id': data.get('lead_id'),
        'status': data.get('status'),
    }


def process_event(event: dict[str, Any]) -> dict[str, Any]:
    """Process CRM event.
    Args:
        event (dict[str, Any]): Parsed event data."""
    if event['event'] == 'lead.updated':
        print(f"Lead aktualisiert: {event['lead_id']}")

    if event['event'] == 'lead.created':
        print(f"Neuer Lead: {event['lead_id']}")

    return event


@app.post('/crm/webhook')
async def receive_webhook(request: Request) -> dict[str, str]:
    """Receive CRM webhook event.
    Args:
        request (Request): Incoming HTTP request."""
    payload = await request.json()

    event = parse_event(payload=payload)
    process_event(event=event)

    return {'status': 'received'}
