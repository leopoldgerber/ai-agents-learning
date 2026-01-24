import asyncio
import json
import logging
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse


app = FastAPI()

logger = logging.getLogger('uvicorn.error')


def build_message_payload(message_index: int) -> str:
    """Build a minimal JSON payload for SSE message.
    Args:
        message_index (int): Index of the message in the demo stream."""
    payload = {'text': f'message {message_index}'}
    return json.dumps(payload, ensure_ascii=False)


def build_heartbeat_payload() -> str:
    """Build a minimal JSON payload for SSE heartbeat.
    Args:
        None: No args."""
    payload = {'type': 'heartbeat'}
    return json.dumps(payload, ensure_ascii=False)


def build_sse_event(event_id: str, event_type: str, data: str) -> str:
    """Build a single SSE event block.
    Args:
        event_id (str): Event identifier for reconnection support.
        event_type (str): Event type name for routing on the client side.
        data (str): Data payload as a string (commonly JSON)."""
    return f'id: {event_id}\nevent: {event_type}\ndata: {data}\n\n'


def parse_last_event_id(request: Request) -> int:
    """Parse Last-Event-ID header from request.
    Args:
        request (Request): FastAPI request with headers."""
    last_event_id = request.headers.get('last-event-id')
    if last_event_id is None:
        return 0
    if not last_event_id.isdigit():
        return 0
    return int(last_event_id) + 1


async def generate_message_events(
    start_index: int,
    end_index: int,
) -> AsyncGenerator[str, None]:
    """Generate message events for the demo stream.
    Args:
        start_index (int): Start index for messages.
        end_index (int): End index (exclusive) for messages."""
    for i in range(start_index, end_index):
        payload_json = build_message_payload(message_index=i)
        yield build_sse_event(event_id=str(i), event_type='message', data=payload_json)
        await asyncio.sleep(1)


async def generate_heartbeat_events(
    start_event_id: int,
    interval_seconds: float,
) -> AsyncGenerator[str, None]:
    """Generate heartbeat events on a fixed interval.
    Args:
        start_event_id (int): Starting id for heartbeat events.
        interval_seconds (float): Heartbeat interval in seconds."""
    heartbeat_id = start_event_id
    while True:
        payload_json = build_heartbeat_payload()
        yield build_sse_event(event_id=str(heartbeat_id), event_type='heartbeat', data=payload_json)
        heartbeat_id += 1
        await asyncio.sleep(interval_seconds)


async def event_stream(request: Request, start_index: int) -> Any:
    """Stream SSE events until client disconnects.
    Args:
        request (Request): FastAPI request for client context.
        start_index (int): Start index for demo messages."""
    message_end_index = 5
    heartbeat_interval_seconds = 5.0

    try:
        async for message_event in generate_message_events(
            start_index=start_index,
            end_index=message_end_index,
        ):
            if await request.is_disconnected():
                logger.info('Client disconnected during message stream')
                return
            yield message_event

        async for heartbeat_event in generate_heartbeat_events(
            start_event_id=message_end_index,
            interval_seconds=heartbeat_interval_seconds,
        ):
            if await request.is_disconnected():
                logger.info('Client disconnected during heartbeat')
                return
            yield heartbeat_event
    except asyncio.CancelledError:
        logger.info('Client disconnected (stream cancelled)')
        raise


@app.get('/stream')
async def stream(request: Request) -> StreamingResponse:
    start_index = parse_last_event_id(request=request)
    logger.info('Client connected to /stream endpoint')
    return StreamingResponse(
        event_stream(request=request, start_index=start_index),
        media_type='text/event-stream',
    )
