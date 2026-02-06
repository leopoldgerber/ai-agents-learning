# Redis: Caching (3.2.2.1)

## About This Module

This module introduces Redis as an **in-memory cache** in the context of database-backed systems.
It demonstrates the most common caching approach used in API services: **cache-aside**.

The goal is to show how Redis can reduce latency and load on primary storage by serving frequently requested data from memory, while keeping the example minimal and educational.

---

## Why Caching Matters

In real systems, the same data is often requested repeatedly:

* user profiles,
* feature flags,
* configuration and lookup tables,
* product details,
* aggregated metrics.

If every request hits the primary database or an external API:

* latency increases,
* throughput decreases,
* costs go up,
* the system becomes more fragile under spikes.

Caching helps ensure:

> **Hot reads → served from memory**

while the database remains the source of truth.

---

## Core Idea

This module uses the **cache-aside** pattern:

1. Build a cache key
2. Try to read from Redis (`GET`)
3. If missing (cache miss), load from the source
4. Store in Redis with a TTL (`SET ... EX ttl`)
5. Return the result

TTL (time-to-live) makes cached data **self-expiring**, preventing permanent staleness and limiting memory usage.

---

## Implemented Example

### Cache-Aside with TTL

**File:** `redis_cache_demo.py`

What it demonstrates:

* Redis client initialization from `.env`
* building a stable cache key
* reading cached JSON (`GET`)
* writing cached JSON with expiration (`SET` + `ex`)
* two sequential calls:

  * first call → cache miss → loads from “DB” (simulated)
  * second call → cache hit → returns from Redis

This mirrors how API handlers typically cache user data.

---

## Environment Variables

The script reads Redis connection parameters from `.env`:

* `REDIS_HOST` (default: `localhost`)
* `REDIS_PORT` (default: `6379`)
* `REDIS_DB` (default: `0`)
* `REDIS_PASSWORD` (optional)

---

## Running the Demo

1. Ensure Redis is running locally (or configure your connection in `.env`).
2. Run the script:

```bash
python redis_cache_demo.py
```

Expected behavior:

* `first_call` reports `source: "db"`
* `second_call` reports `source: "cache"`

---

## What This Module Does NOT Cover

To keep the lesson focused, the following topics are intentionally not included:

* cache invalidation strategies (manual vs event-based)
* stampede protection (locks, single-flight)
* distributed consistency guarantees
* write-through / write-behind caching
* caching large objects and memory tuning

These are natural next steps after understanding cache-aside.

---

## Educational Focus

This module emphasizes:

* the difference between **source of truth** (DB) and **fast read path** (Redis)
* how TTL controls staleness and storage growth
* building deterministic cache keys
* designing cache behavior that remains safe under retries

The code favors clarity over abstraction.

---

## Position in the Course

This lesson begins the Redis block:

* caching → fast reads and reduced load
* queues → background processing patterns
* rate-limit storage → enforcing API limits with shared state

Together, these patterns form a practical Redis toolkit for service and agent architectures.
