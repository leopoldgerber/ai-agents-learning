import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse


app = FastAPI()
logger = logging.getLogger('uvicorn.error')


def build_sse_event(event_type: str, data: str, event_id: int) -> str:
    """Build a single SSE event block.
    Args:
        event_type (str): SSE event type name.
        data (str): Event payload as a string.
        event_id (int): Incremental event identifier."""
    return f'id: {event_id}\nevent: {event_type}\ndata: {data}\n\n'


def build_message_data(index: int) -> str:
    """Build JSON payload for message events.
    Args:
        index (int): Message index."""
    payload = {'text': f'message {index}'}
    return json.dumps(payload, ensure_ascii=False)


def build_heartbeat_data() -> str:
    """Build JSON payload for heartbeat events.
    Args:
        None: No arguments."""
    payload = {'type': 'heartbeat'}
    return json.dumps(payload, ensure_ascii=False)


async def sse_event_stream(request: Request) -> AsyncGenerator[str, None]:
    """Generate SSE events until client disconnects.
    Args:
        request (Request): FastAPI request object."""
    event_index = 0

    for _ in range(5):
        if await request.is_disconnected():
            logger.info('Client disconnected during message stream')
            return

        yield build_sse_event(
            event_type='message',
            data=build_message_data(event_index),
            event_id=event_index,
        )
        event_index += 1
        await asyncio.sleep(1)

    while True:
        if await request.is_disconnected():
            logger.info('Client disconnected during heartbeat stream')
            return

        yield build_sse_event(
            event_type='heartbeat',
            data=build_heartbeat_data(),
            event_id=event_index,
        )
        event_index += 1
        await asyncio.sleep(5)


@app.get('/health')
async def health() -> dict[str, bool]:
    """Health check endpoint.
    Args:
        None: No arguments."""
    return {'ok': True}


@app.get('/stream')
async def stream(request: Request) -> StreamingResponse:
    """SSE endpoint demonstrating one-way server-to-client streaming.
    Args:
        request (Request): FastAPI request object."""
    logger.info('Client connected to /stream endpoint')
    return StreamingResponse(
        sse_event_stream(request=request),
        media_type='text/event-stream',
    )
