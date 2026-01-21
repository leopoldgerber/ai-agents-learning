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


async def event_stream() -> Any:
    for i in range(5):
        payload_json = build_message_payload(message_index=i)
        yield f'data: {payload_json}\n\n'
        await asyncio.sleep(1)


@app.get('/stream')
async def stream() -> StreamingResponse:
    return StreamingResponse(event_stream(), media_type='text/event-stream')
