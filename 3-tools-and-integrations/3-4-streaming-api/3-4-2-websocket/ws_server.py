import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

logger = logging.getLogger("uvicorn.error")


def build_ws_event(event_type: str, payload: dict[str, Any]) -> str:
    """Build a minimal JSON event message for WebSocket.
    Args:
        event_type (str): Event type name.
        payload (dict[str, Any]): Message payload."""
    message = {
        "event_type": event_type,
        "ts": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    return json.dumps(message, ensure_ascii=False)


def parse_ws_command(raw_text: str) -> dict[str, Any]:
    """Parse client command from raw text.
    Args:
        raw_text (str): Raw text received from WebSocket."""
    return json.loads(raw_text)


def parse_run_id(command: dict[str, Any]) -> str | None:
    """Parse run_id from a command payload.
    Args:
        command (dict[str, Any]): Parsed command object."""
    run_id = command.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        return None
    return run_id


async def stream_run_events(ws: WebSocket, run_id: str) -> None:
    """Stream demo run events to the client.
    Args:
        ws (WebSocket): WebSocket connection.
        run_id (str): Run identifier."""
    try:
        for i in range(5):
            await ws.send_text(
                build_ws_event(
                    event_type="run_event",
                    payload={
                        "run_id": run_id,
                        "step": i,
                        "text": f"agent step {i}"},
                )
            )
            await asyncio.sleep(1)

        await ws.send_text(
            build_ws_event(event_type="run_done", payload={"run_id": run_id})
        )
    except asyncio.CancelledError:
        await ws.send_text(
            build_ws_event(
                event_type="run_cancelled", payload={"run_id": run_id})
        )
        raise


@app.get("/health")
async def health() -> dict[str, bool]:
    """Health check endpoint.
    Args:
        None: No args."""
    return {"ok": True}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    """WebSocket endpoint supporting multi-run agent-style protocol.
    Args:
        ws (WebSocket): WebSocket connection."""
    await ws.accept()
    logger.info("WebSocket client connected")

    run_tasks: dict[str, asyncio.Task[None]] = {}

    try:
        await ws.send_text(
            build_ws_event(
                event_type="connected",
                payload={"message": "Connected"}
            )
        )

        while True:
            raw_text = await ws.receive_text()
            command = parse_ws_command(raw_text=raw_text)

            command_type = command.get("command")

            if command_type == "start_run":
                run_id = parse_run_id(command=command)
                if run_id is None:
                    await ws.send_text(
                        build_ws_event(
                            event_type="error",
                            payload={"message": "run_id is required"},
                        )
                    )
                    continue

                existing_task = run_tasks.get(run_id)
                if existing_task is not None and not existing_task.done():
                    await ws.send_text(
                        build_ws_event(
                            event_type="error",
                            payload={
                                "message": "Run already in progress",
                                "run_id": run_id,
                            },
                        )
                    )
                    continue

                await ws.send_text(
                    build_ws_event(
                        event_type="run_started",
                        payload={"run_id": run_id}
                    )
                )
                run_tasks[run_id] = asyncio.create_task(
                    stream_run_events(ws=ws, run_id=run_id)
                )
                continue

            if command_type == "cancel_run":
                run_id = parse_run_id(command=command)
                if run_id is None:
                    await ws.send_text(
                        build_ws_event(
                            event_type="error",
                            payload={"message": "run_id is required"},
                        )
                    )
                    continue

                task = run_tasks.get(run_id)
                if task is None or task.done():
                    await ws.send_text(
                        build_ws_event(
                            event_type="error",
                            payload={
                                "message": "No active run to cancel",
                                "run_id": run_id,
                            },
                        )
                    )
                    continue

                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                continue

            await ws.send_text(
                build_ws_event(
                    event_type="error",
                    payload={
                        "message": "Unknown command",
                        "received": command
                    },
                )
            )

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    finally:
        for task in run_tasks.values():
            if not task.done():
                task.cancel()
