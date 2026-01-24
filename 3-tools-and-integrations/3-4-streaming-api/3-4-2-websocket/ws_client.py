import asyncio
import json
from typing import Any

import websockets


def parse_ws_event(raw_text: str) -> dict[str, Any]:
    """Parse server message into a dict.
    Args:
        raw_text (str): Raw text received from WebSocket."""
    return json.loads(raw_text)


def build_command(command: dict[str, Any]) -> str:
    """Build a command message as JSON string.
    Args:
        command (dict[str, Any]): Command payload."""
    return json.dumps(command, ensure_ascii=False)


async def run_ws_client(url: str) -> None:
    """Connect to WebSocket, start two runs, cancel one, and print events.
    Args:
        url (str): WebSocket URL."""
    async with websockets.connect(url) as websocket:
        connected_msg = await websocket.recv()
        print("RECV:", parse_ws_event(raw_text=connected_msg))

        await websocket.send(
            build_command({"command": "start_run", "run_id": "run-001"})
        )
        await websocket.send(
            build_command({"command": "start_run", "run_id": "run-002"})
        )

        await asyncio.sleep(2.5)
        await websocket.send(
            build_command({"command": "cancel_run", "run_id": "run-002"})
        )

        done_or_cancelled: set[str] = set()

        while True:
            server_msg = await websocket.recv()
            event = parse_ws_event(raw_text=server_msg)
            print("RECV:", event)

            event_type = event.get("event_type")
            run_id = event.get("payload", {}).get("run_id")

            if (
                event_type in {"run_done", "run_cancelled"}
                and isinstance(run_id, str)
            ):
                done_or_cancelled.add(run_id)

            if done_or_cancelled.issuperset({"run-001", "run-002"}):
                break


if __name__ == "__main__":
    ws_url = "ws://localhost:8000/ws"
    asyncio.run(run_ws_client(url=ws_url))
