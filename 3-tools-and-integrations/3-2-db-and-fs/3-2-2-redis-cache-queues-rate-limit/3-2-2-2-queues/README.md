# Redis: Queues (3.2.2.2)

## About This Module

This module demonstrates how **Redis lists** can be used to implement a **simple task queue**.
The goal is to show the core mechanics of producer–consumer interaction using Redis primitives,
without introducing external brokers or complex abstractions.

The example is intentionally minimal and focuses on understanding **what actually happens in Redis**
when tasks are enqueued and consumed.

---

## Why Queues Are Needed

Queues are used when:

* work must be processed asynchronously,
* tasks may take time or fail,
* producers and consumers must be decoupled,
* workload should be smoothed over time.

Typical use cases:

* sending emails,
* processing webhooks,
* background data processing,
* scheduled or delayed jobs,
* offloading heavy work from API requests.

---

## Core Idea

Redis provides **lists**, which can be used as FIFO queues:

* producer → pushes tasks into a list
* worker → pops tasks from the list

In this module:

* `RPUSH` is used to enqueue tasks (push to the right)
* `BLPOP` is used to consume tasks (blocking pop from the left)

This creates a classic queue behavior.

---

## Implemented Example

### Producer

**File:** `redis_queue_producer.py`

What it does:

1. Builds a Redis client from `.env`
2. Creates task payloads as JSON strings
3. Pushes multiple tasks into a Redis list using `RPUSH`
4. Receives the **new length of the queue** from Redis

Important detail:

> `RPUSH` returns the length of the list **after** insertion.

This allows the producer to understand the current size of the queue
without an additional `LLEN` call.

---

### Worker

**File:** `redis_queue_worker.py`

What it does:

1. Connects to Redis
2. Waits for tasks using `BLPOP`
3. Blocks until a task appears or timeout expires
4. Decodes and processes tasks one by one

`BLPOP` is used instead of `LPOP` to avoid busy-waiting
and unnecessary CPU usage.

---

## Blocking vs Non-Blocking Pop

* `LPOP` — returns immediately (may return nothing)
* `BLPOP` — waits until a task is available or timeout occurs

Blocking pop is preferred for workers because it:

* reduces CPU usage
* simplifies worker loops
* behaves closer to real message queues

---

## Reliability Considerations

This example demonstrates **basic queues**, but has limitations:

* tasks are removed from the queue immediately on pop
* if a worker crashes during processing, the task is lost

This is acceptable for learning purposes but not for critical workloads.

Production systems usually extend this pattern with:

* processing queues (`RPOPLPUSH` / `BRPOPLPUSH`)
* retries
* dead-letter queues (DLQ)
* idempotent task handlers

---

## Environment Variables

The scripts read Redis connection parameters from `.env`:

* `REDIS_HOST` (default: `localhost`)
* `REDIS_PORT` (default: `6379`)
* `REDIS_DB` (default: `0`)
* `REDIS_PASSWORD` (optional)

---

## Running the Demo

1. Start Redis.
2. Run the producer:

```bash
python redis_queue_producer.py
```

3. In another terminal, run the worker:

```bash
python redis_queue_worker.py
```

Expected behavior:

* producer enqueues tasks
* worker blocks until tasks appear
* tasks are processed sequentially

---

## Educational Focus

This module focuses on:

* understanding Redis lists as queues
* producer–consumer separation
* blocking vs non-blocking operations
* observing queue length as system state

The emphasis is on **mechanics and behavior**, not production hardening.

---

## Position in the Course

This lesson builds on Redis caching and prepares for:

* reliable queue patterns
* rate-limit storage
* distributed coordination primitives

It forms the foundation for understanding Redis as a lightweight message broker.
