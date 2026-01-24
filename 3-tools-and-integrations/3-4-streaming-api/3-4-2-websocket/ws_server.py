import asyncio
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


def parse_ws_command(raw_text: str) -> dict[str, Any]:
    """Parse client command from raw text.
    Args:
        raw_text (str): Raw text received from WebSocket."""
    return json.loads(raw_text)


async def stream_run_events(ws: WebSocket, run_id: str) -> None:
    """Stream demo run events to the client.
    Args:
        ws (WebSocket): WebSocket connection.
        run_id (str): Run identifier."""
    for i in range(5):
        await ws.send_text(
            build_ws_event(
                event_type='run_event',
                payload={'run_id': run_id, 'step': i, 'text': f'agent step {i}'},
            )
        )
        await asyncio.sleep(1)

    await ws.send_text(build_ws_event(event_type='run_done', payload={'run_id': run_id}))


@app.get('/health')
async def health() -> dict[str, bool]:
    """Health check endpoint.
    Args:
        None: No args."""
    return {'ok': True}


@app.websocket('/ws')
async def websocket_endpoint(ws: WebSocket) -> None:
    """WebSocket endpoint supporting a minimal agent-style protocol.
    Args:
        ws (WebSocket): WebSocket connection."""
    await ws.accept()
    logger.info('WebSocket client connected')

    try:
        await ws.send_text(build_ws_event(event_type='connected', payload={'message': 'Connected'}))

        while True:
            raw_text = await ws.receive_text()
            command = parse_ws_command(raw_text=raw_text)

            command_type = command.get('command')
            if command_type != 'start_run':
                await ws.send_text(
                    build_ws_event(
                        event_type='error',
                        payload={'message': 'Unknown command', 'received': command},
                    )
                )
                continue

            run_id = command.get('run_id')
            if not isinstance(run_id, str) or not run_id:
                await ws.send_text(
                    build_ws_event(
                        event_type='error',
                        payload={'message': 'run_id is required', 'received': command},
                    )
                )
                continue

            await ws.send_text(build_ws_event(event_type='run_started', payload={'run_id': run_id}))
            await stream_run_events(ws=ws, run_id=run_id)

    except WebSocketDisconnect:
        logger.info('WebSocket client disconnected')
