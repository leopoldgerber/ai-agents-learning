# API JSON Validation: Contract-First Input Validation

## About This Module

This module focuses on **JSON input validation for API-based tools** using **Pydantic**.
The goal is to demonstrate how strict, explicit validation can serve as a **contract boundary** between an API server and an agent (client).

This step concentrates on **synchronous request–response validation** and error handling — a foundational building block for reliable agent systems.

The implementation is intentionally minimal and educational, while following production-oriented patterns.

---

## Why JSON Validation Matters for Agents

In agent-oriented systems, APIs are rarely consumed by humans directly.
Instead, they are used by **agents, tools, or orchestration layers**, which rely on:

* strict input contracts,
* predictable error structures,
* explicit rejection of invalid data.

Without strong validation:

* agents must guess API behavior,
* errors become implicit and brittle,
* debugging moves from boundaries into internal logic.

This module treats **validation as a first-class concern**, not a side effect.

---

## Implemented Scenario

The module implements a simple validation flow:

1. The **client (agent)** sends JSON payloads to the API.
2. The **server validates raw input** using Pydantic models.
3. Two scenarios are intentionally tested:

   * a **valid payload** (happy path),
   * an **invalid payload** (validation failure).
4. The server:

   * accepts valid input and returns a typed response,
   * rejects invalid input with a structured error description.
5. The client:

   * does not assume success,
   * observes and prints both success and failure responses.

This mirrors how real agents probe and reason about external tools.

---

## Architecture Overview

### Server (`api_json_server.py`)

Responsibilities:

* Accept raw JSON input (`dict[str, Any]`).
* Validate input explicitly using **Pydantic models**.
* Forbid unknown fields (`extra='forbid'`).
* Return:

  * a typed success response on valid input,
  * a structured validation error on invalid input.
* Avoid embedding business or agent logic.

The server acts strictly as a **contract enforcer**.

---

### Client (`api_json_client.py`)

Responsibilities:

* Act as a minimal **agent-style API consumer**.
* Send multiple payloads in a single run:

  * one valid,
  * one invalid.
* Observe HTTP status codes and response bodies.
* Avoid assumptions about success or failure.

The client is intentionally simple and runnable as a script.

---

## File Structure

```
3-3-api-json-validation/
├── api_json_server.py   # API server with strict Pydantic validation
├── api_json_client.py   # Minimal agent-style client for contract testing
└── README.md            # Module description
```

---

## How to Run

1. Start the API server:

```bash
make 3-3-server
```

2. In a separate terminal, run the client:

```bash
make 3-3-client
```

The client will:

* send a valid JSON payload and receive `200 OK`,
* send an invalid payload and receive `400 Validation Error`,
* print both responses for inspection.

---

## Implementation Notes

* This is an **educational example**, not a production-ready API.
* Validation is performed explicitly via Pydantic, not implicitly via framework magic.
* Multiple validation errors are returned in a single response to provide full feedback.
* The server does not attempt to recover from invalid input — it rejects it early.
* This pattern scales naturally to:

  * tool APIs,
  * agent function calling,
  * schema-based orchestration layers.

---

## Position in the Course

This module completes the **API validation foundation** within the
`Tools and Integrations` stage.

It prepares the ground for:

* tool-based agents,
* schema-driven execution,
* explicit contracts between reasoning and execution layers.
