import asyncio
import json
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse


app = FastAPI()


def build_message_payload(message_index: int) -> str:
    """Build a minimal JSON payload for SSE message.
    Args:
        message_index (int): Index of the message in the demo stream."""
    payload = {'text': f'message {message_index}'}
    return json.dumps(payload, ensure_ascii=False)


def build_sse_event(event_id: str, event_type: str, data: str) -> str:
    """Build a single SSE event block.
    Args:
        event_id (str): Event identifier for reconnection support.
        event_type (str): Event type name for routing on the client side.
        data (str): Data payload as a string (commonly JSON)."""
    return f'id: {event_id}\nevent: {event_type}\ndata: {data}\n\n'


async def event_stream() -> Any:
    for i in range(5):
        payload_json = build_message_payload(message_index=i)
        yield build_sse_event(
            event_id=str(i),
            event_type='message',
            data=payload_json
        )
        await asyncio.sleep(1)


@app.get('/stream')
async def stream() -> StreamingResponse:
    return StreamingResponse(event_stream(), media_type='text/event-stream')
