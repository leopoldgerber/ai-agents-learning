# Server-Sent Events (SSE): Streaming for Agent Systems

## About This Module

This module explores **Server-Sent Events (SSE)** as a mechanism for server-to-client streaming in the context of agent-based systems. SSE provides a simple, HTTP-based way to continuously push events from a server to a client over a single long-lived connection.

The implementation is intentionally educational and engineering-focused: it demonstrates how to build a robust SSE stream step by step, while keeping responsibilities between server and client clearly separated.

---

## When and Why to Use SSE

SSE is best suited for scenarios where:

* The client needs to **receive a continuous stream of events**.
* Communication is **one-directional** (server → client).
* Simplicity and HTTP compatibility are preferred over full duplex communication.

In agent systems, SSE is a natural fit for:

* progress updates,
* logs and traces,
* token or reasoning streams,
* monitoring long-running agent executions.

Compared to WebSocket, SSE intentionally limits interaction to simplify the transport layer.

---

## Implemented Scenario

This module implements a progressively enhanced SSE server:

* A single `/stream` endpoint that keeps an HTTP connection open.
* Structured SSE events with:

  * `id` for ordering and resuming,
  * `event` for event typing,
  * `data` as a JSON payload.
* **Heartbeat events** to keep the connection alive.
* Proper handling of client disconnects.
* Support for `Last-Event-ID` to resume streams.
* An in-memory **backlog buffer** for replaying missed events.
* Stream isolation using a `topic` query parameter.

A minimal client is provided to validate and observe the stream behavior.

---

## Architecture Overview

**Server (`sse_server.py`)**:

* Exposes an SSE endpoint using `StreamingResponse`.
* Acts as a *data source only* — no agent logic is embedded.
* Generates different event types (`message`, `heartbeat`).
* Maintains an in-memory buffer of recent events.
* Supports resuming streams via `Last-Event-ID`.

**Client (`sse_client.py`)**:

* Opens a single HTTP connection to the SSE endpoint.
* Consumes and prints raw SSE events.
* Does not interpret agent logic (this is handled at higher layers).

This separation mirrors real agent architectures, where transport and reasoning are decoupled.

---

## File Structure

```
3-4-1-sse/
├── sse_server.py   # SSE server with buffering, heartbeat, and resume support
├── sse_client.py   # Minimal SSE client for observing the stream
└── README.md       # Module description
```

---

## How to Run

1. Start the SSE server:

```bash
make sse-server
```

2. In a separate terminal, start the client:

```bash
make sse-client
```

The client will:

* connect to the `/stream` endpoint,
* print incoming SSE events,
* continue receiving heartbeat events after messages are exhausted.

You can experiment with reconnections by restarting the client and providing `Last-Event-ID`.

---

## Implementation Notes

* This is an **educational example**, not a production-ready SSE service.
* The event buffer is stored in memory and resets on server restart.
* The server is intentionally stateless with respect to agent logic.
* Heartbeat events are essential for keeping connections alive through proxies and load balancers.
* SSE is designed for simplicity; more interactive control flows should use WebSocket instead.
