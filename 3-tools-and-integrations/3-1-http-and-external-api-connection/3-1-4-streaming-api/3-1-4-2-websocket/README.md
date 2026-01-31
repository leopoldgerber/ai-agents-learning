# WebSocket: Agent-Style Streaming

## About This Module

This module focuses on using **WebSocket** for bidirectional communication between a client and a server in the context of agent-based systems. Unlike SSE, WebSocket allows not only streaming events from the server to the client, but also receiving commands from the client in real time.

The module is implemented as an educational, engineering-oriented example: the code is intentionally simple, but architecturally correct and designed to be extended step by step.

---

## How WebSocket Differs from SSE

Key differences that are especially important for agent-oriented scenarios:

* **Bidirectional channel**: the client can send commands, and the server can react and stream events back.
* **Connection state**: the server actively manages the lifecycle of executions (runs).
* **Interactivity**: cancellation, control commands, and parallel executions are possible.
* **No HTTP streaming**: after the handshake, communication happens over the WebSocket protocol.

SSE is better suited for passive data consumption, while WebSocket is a better fit for agent control and coordination.

---

## Implemented Scenario

This example implements a simplified agent-style protocol:

* The client connects via WebSocket.
* The client sends a `start_run` command with a `run_id`.
* The server starts an asynchronous execution and streams `run_event` events.
* **Multiple runs can execute in parallel** within a single connection.
* The client can send a `cancel_run` command for a specific `run_id`.
* The server correctly completes or cancels each run.

All events include an `event_type`, a server-side timestamp, and a `payload`.

---

## Architecture Overview

**Server (`ws_server.py`)**:

* Accepts WebSocket connections.
* Maintains a mapping of active `run_id → asyncio.Task`.
* Handles control commands:

  * `start_run`
  * `cancel_run`
* Streams execution events back to the client.

**Client (`ws_client.py`)**:

* Establishes a WebSocket connection.
* Sends control commands to the server.
* Listens for incoming events and routes them by `run_id`.

The architecture deliberately avoids connection managers or message queues — those are introduced at more advanced stages.

---

## File Structure

```
3-4-2-websocket/
├── ws_server.py   # WebSocket server with agent-style protocol
├── ws_client.py   # Simple client to start and control runs
└── README.md      # Module description
```

---

## How to Run

1. Start the server:

```bash
make ws-server
```

2. In a separate terminal, start the client:

```bash
make ws-client
```

The client will:

* start multiple runs,
* cancel one of them,
* print all received events to the console.

---

## Implementation Notes

* This is an **educational example**, not a production-ready server.
* Messages are sent directly from multiple `asyncio.Task` instances; in real systems, a single sender loop is recommended.
* Connection-local state (`run_tasks`) keeps the example simple but does not scale horizontally.
* The WebSocket protocol defined here is minimal and intended to demonstrate core ideas rather than completeness.
