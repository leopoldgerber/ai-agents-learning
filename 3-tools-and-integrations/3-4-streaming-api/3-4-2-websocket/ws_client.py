import asyncio
import json
from typing import Any

import websockets


def parse_ws_event(raw_text: str) -> dict[str, Any]:
    """Parse server message into a dict.
    Args:
        raw_text (str): Raw text received from WebSocket."""
    return json.loads(raw_text)


async def run_ws_client(url: str) -> None:
    """Connect to WebSocket, receive initial message,
    send one message, receive echo.
    Args:
        url (str): WebSocket URL."""
    async with websockets.connect(url) as websocket:
        connected_msg = await websocket.recv()
        print('RECV:', parse_ws_event(raw_text=connected_msg))

        await websocket.send('hello from ws_client')
        echo_msg = await websocket.recv()
        print('RECV:', parse_ws_event(raw_text=echo_msg))


if __name__ == '__main__':
    ws_url = 'ws://127.0.0.1:8000/ws'
    asyncio.run(run_ws_client(url=ws_url))
