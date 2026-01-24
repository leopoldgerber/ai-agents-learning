import asyncio
import json
import logging
from collections import deque
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse


app = FastAPI()

logger = logging.getLogger('uvicorn.error')

events_lock = asyncio.Lock()
events_buffer: deque[dict[str, str]] = deque(maxlen=200)


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


async def append_buffered_event(event_id: int, event_type: str, data: str) -> None:
    """Append a streamed event to in-memory buffer.
    Args:
        event_id (int): Event identifier.
        event_type (str): SSE event type.
        data (str): SSE data payload."""
    async with events_lock:
        events_buffer.append(
            {
                'id': str(event_id),
                'type': event_type,
                'data': data,
            }
        )


async def read_buffered_events(start_event_id: int) -> list[dict[str, str]]:
    """Read buffered events starting from a given id (inclusive).
    Args:
        start_event_id (int): First event id to return."""
    async with events_lock:
        return [event for event in list(events_buffer) if int(event['id']) >= start_event_id]


async def read_last_buffered_id() -> int | None:
    """Read the last buffered event id, if any.
    Args:
        None: No args."""
    async with events_lock:
        if not events_buffer:
            return None
        return int(events_buffer[-1]['id'])


async def generate_message_events(
    start_event_id: int,
    end_event_id: int,
) -> AsyncGenerator[str, None]:
    """Generate message events for the demo stream.
    Args:
        start_event_id (int): Start event id for messages.
        end_event_id (int): End event id (exclusive) for messages."""
    for event_id in range(start_event_id, end_event_id):
        payload_json = build_message_payload(message_index=event_id)
        await append_buffered_event(event_id=event_id, event_type='message', data=payload_json)
        yield build_sse_event(event_id=str(event_id), event_type='message', data=payload_json)
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
        await append_buffered_event(event_id=heartbeat_id, event_type='heartbeat', data=payload_json)
        yield build_sse_event(event_id=str(heartbeat_id), event_type='heartbeat', data=payload_json)
        heartbeat_id += 1
        await asyncio.sleep(interval_seconds)


async def event_stream(request: Request, start_index: int) -> Any:
    """Stream SSE events until client disconnects.
    Args:
        request (Request): FastAPI request for client context.
        start_index (int): Next event id to start streaming from."""
    message_end_event_id = 5
    heartbeat_interval_seconds = 5.0

    try:
        buffered_events = await read_buffered_events(start_event_id=start_index)
        if buffered_events:
            for event in buffered_events:
                if await request.is_disconnected():
                    logger.info('Client disconnected during backlog replay')
                    return
                yield build_sse_event(event_id=event['id'], event_type=event['type'], data=event['data'])

            last_buffered_id = await read_last_buffered_id()
            next_event_id = int(last_buffered_id) + 1 if last_buffered_id is not None else start_index
        else:
            next_event_id = start_index

        if next_event_id < message_end_event_id:
            async for message_event in generate_message_events(
                start_event_id=next_event_id,
                end_event_id=message_end_event_id,
            ):
                if await request.is_disconnected():
                    logger.info('Client disconnected during message stream')
                    return
                yield message_event
            next_event_id = message_end_event_id

        async for heartbeat_event in generate_heartbeat_events(
            start_event_id=next_event_id,
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
