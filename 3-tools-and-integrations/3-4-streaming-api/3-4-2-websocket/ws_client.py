import asyncio
import json
from typing import Any

import websockets


def parse_ws_event(raw_text: str) -> dict[str, Any]:
    """Parse server message into a dict.
    Args:
        raw_text (str): Raw text received from WebSocket."""
    return json.loads(raw_text)


def build_start_run_command(run_id: str) -> str:
    """Build a start_run command message.
    Args:
        run_id (str): Run identifier."""
    command = {'command': 'start_run', 'run_id': run_id}
    return json.dumps(command, ensure_ascii=False)


async def run_ws_client(url: str, run_id: str) -> None:
    """Connect to WebSocket, start a run, and print streamed events.
    Args:
        url (str): WebSocket URL.
        run_id (str): Run identifier."""
    async with websockets.connect(url) as websocket:
        connected_msg = await websocket.recv()
        print('RECV:', parse_ws_event(raw_text=connected_msg))

        await websocket.send(build_start_run_command(run_id=run_id))

        while True:
            server_msg = await websocket.recv()
            event = parse_ws_event(raw_text=server_msg)
            print('RECV:', event)

            if event.get('event_type') == 'run_done':
                break


if __name__ == '__main__':
    ws_url = 'ws://localhost:8000/ws'
    asyncio.run(run_ws_client(url=ws_url, run_id='run-001'))
