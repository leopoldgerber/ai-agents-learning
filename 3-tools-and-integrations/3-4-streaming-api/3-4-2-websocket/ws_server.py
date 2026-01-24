import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect


app = FastAPI()

logger = logging.getLogger('uvicorn.error')


def build_ws_event(event_type: str, payload: dict[str, Any]) -> str:
    """Build a minimal JSON event message for WebSocket.
    Args:
        event_type (str): Event type name.
        payload (dict[str, Any]): Message payload."""
    message = {
        'event_type': event_type,
        'ts': datetime.now(timezone.utc).isoformat(),
        'payload': payload,
    }
    return json.dumps(message, ensure_ascii=False)


@app.get('/health')
async def health() -> dict[str, bool]:
    """Health check endpoint.
    Args:
        None: No args."""
    return {'ok': True}


@app.websocket('/ws')
async def websocket_endpoint(ws: WebSocket) -> None:
    """WebSocket endpoint: accept connection and echo messages back.
    Args:
        ws (WebSocket): WebSocket connection."""
    await ws.accept()
    logger.info('WebSocket client connected')

    try:
        await ws.send_text(build_ws_event(event_type='connected', payload={'message': 'Connected'}))

        while True:
            raw_text = await ws.receive_text()
            await ws.send_text(build_ws_event(event_type='echo', payload={'text': raw_text}))
    except WebSocketDisconnect:
        logger.info('WebSocket client disconnected')
