from fastapi import FastAPI, HTTPException, Request
from utils import is_duplicate_event, verify_signature


app = FastAPI()


def process_event_async(event: dict) -> dict:
    """Process event placeholder.
    Args:
        event (dict): Parsed webhook event data."""
    return event


@app.post('/crm/webhook')
async def crm_webhook(request: Request) -> dict[str, str]:
    """Receive and handle CRM webhooks.
    Args:
        request (Request): Incoming HTTP request."""
    body = await request.body()
    signature = request.headers.get('X-Signature')

    if not verify_signature(body, signature):
        raise HTTPException(status_code=401, detail='Invalid signature')

    event = await request.json()
    event_id = str(event.get('id', ''))

    if is_duplicate_event(event_id):
        return {'status': 'duplicate'}

    process_event_async(event)
    return {'status': 'ok'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8000)
