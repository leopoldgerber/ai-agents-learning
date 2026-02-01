# Webhooks: Deduplication (3.1.5.3)

## About This Module

This module focuses on **deduplication of incoming events** in HTTP-based integrations.
It demonstrates how a system can safely handle **repeated deliveries of the same event** — a situation that naturally arises due to **retries**, timeouts, or network failures.

The goal is to show how **idempotency and state tracking** protect business logic from being executed multiple times for the same event.

The examples are intentionally minimal, educational, and aligned with production-grade architectural thinking.

---

## Why Deduplication Matters

In webhook-driven and event-based systems, **delivery is not guaranteed to be exactly once**.
External providers may:

* retry delivery after timeouts,
* resend events after temporary failures,
* deliver the same event to multiple instances.

Without deduplication:

* payments may be charged twice,
* emails may be sent multiple times,
* state transitions may become inconsistent.

Deduplication ensures:

> **One logical event → one business effect**

regardless of how many times the event is delivered.

---

## Core Idea

All implementations in this module rely on the same principle:

* every event has a **globally unique `event_id`**,
* the system records whether this `event_id` was already seen,
* repeated events are detected and ignored before business logic runs.

Retries are handled by the sender.
Deduplication is the responsibility of the receiver.

---

## Implemented Variants

This module demonstrates **three deduplication strategies**, each with different trade-offs.

### 1. In-Memory Deduplication

**File:** `in_memory_dedup.py`

* Uses a Python `set` to store processed `event_id`s.
* Extremely simple and fast.
* Suitable for:

  * local development,
  * learning and experimentation,
  * single-process scripts.

**Limitations:**

* State is lost on process restart.
* Does not work with multiple instances.
* No automatic expiration (TTL).

---

### 2. Redis-Based Deduplication (Key + TTL)

**File:** `redis_dedup.py`

* Uses Redis as a shared, external state store.

* Deduplication is performed via an **atomic** operation:

  * `SET key NX EX ttl`

* TTL ensures automatic cleanup of old events.

Suitable for:

* horizontally scaled services,
* webhook endpoints under retry pressure,
* systems requiring short- to medium-term memory of events.

This approach represents a **common production baseline**.

---

### 3. Database-Backed Deduplication

**File:** `db_dedup.py`

* Stores `event_id` in a database table with a **unique constraint**.
* Deduplication is enforced transactionally by the database.
* Uses `INSERT ... ON CONFLICT DO NOTHING` to detect duplicates.

Suitable for:

* systems requiring auditability,
* strong consistency guarantees,
* long-term retention of event history.

This approach integrates naturally with **Inbox / Outbox** patterns.

---

## Processing Order (Critical)

All variants follow the same safe processing order:

1. Receive request
2. Validate authenticity (signature)
3. Extract `event_id`
4. **Check and record deduplication state**
5. Execute business logic
6. Return `2xx` response

Deduplication must occur **before** business logic.
Violating this order leads to double execution under retries.

---

## What This Module Does NOT Cover

To keep the examples focused, the following topics are intentionally excluded:

* signature verification (covered earlier in the lesson),
* full webhook HTTP handlers,
* background workers and queues,
* exactly-once guarantees across distributed systems.

Those topics build naturally on top of the patterns shown here.

---

## Educational Focus

This module emphasizes:

* clear separation between **delivery** and **processing**,
* explicit state handling instead of implicit assumptions,
* understanding failure modes between retries and side effects.

The code favors clarity over abstraction.
Each file can be read top-to-bottom without external dependencies.

---

## Position in the Course

This lesson completes the **reliability foundation** of webhook integrations:

* signatures → authenticity
* retries → delivery guarantees
* deduplication → execution safety

Together, these concepts form the baseline for building **robust, event-driven integrations** in agent-based and service-oriented systems.
