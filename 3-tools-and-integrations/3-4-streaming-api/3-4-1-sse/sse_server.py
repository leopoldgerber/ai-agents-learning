import asyncio
import json
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()


def build_message_payload(message_index: int) -> str:
    """Build a minimal JSON payload for SSE message.
    Args:
        message_index (int): Index of the message in the demo stream."""
    payload = {"text": f"message {message_index}"}
    return json.dumps(payload, ensure_ascii=False)


def build_sse_event(event_id: str, event_type: str, data: str) -> str:
    """Build a single SSE event block.
    Args:
        event_id (str): Event identifier for reconnection support.
        event_type (str): Event type name for routing on the client side.
        data (str): Data payload as a string (commonly JSON)."""
    return f"id: {event_id}\nevent: {event_type}\ndata: {data}\n\n"


def parse_last_event_id(request: Request) -> int:
    """Parse Last-Event-ID header from request.
    Args:
        request (Request): FastAPI request with headers."""
    last_event_id = request.headers.get("last-event-id")
    if last_event_id is None:
        return 0
    if not last_event_id.isdigit():
        return 0
    return int(last_event_id) + 1


async def event_stream(start_index: int) -> Any:
    for i in range(start_index, 5):
        payload_json = build_message_payload(message_index=i)
        yield build_sse_event(
            event_id=str(i),
            event_type="message",
            data=payload_json
        )
        await asyncio.sleep(1)


@app.get("/stream")
async def stream(request: Request) -> StreamingResponse:
    start_index = parse_last_event_id(request=request)
    return StreamingResponse(
        event_stream(start_index=start_index),
        media_type="text/event-stream",
    )
