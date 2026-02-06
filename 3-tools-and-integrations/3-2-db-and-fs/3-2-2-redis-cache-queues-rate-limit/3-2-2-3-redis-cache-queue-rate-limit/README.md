# Redis: Rate Limiting (3.2.2.3)

## About This Module

This module demonstrates how **Redis can be used as shared rate-limit storage**
for controlling how often a client is allowed to perform an action.

The example focuses on the simplest and most common approach:
**fixed window rate limiting** using Redis atomic counters and TTL.

The goal is not to build a production-ready limiter, but to clearly understand
**how rate limiting works under the hood**.

---

## Why Rate Limiting Is Needed

Rate limiting protects systems from:

* abuse and brute-force attacks,
* accidental overload,
* misbehaving clients or bots,
* cascading failures under high load.

Typical use cases:

* API request limits per client or token,
* login attempt limits,
* webhook retry protection,
* background job throttling.

---

## Core Idea

For each client, Redis stores a **counter key**:

```
rate_limit:<client_id>
```

The logic per request:

1. Increment the counter (`INCR`)
2. If this is the first request, set a TTL (`EXPIRE`)
3. Compare the counter with the allowed limit
4. Allow or deny the request

When the TTL expires, Redis deletes the key automatically,
and the rate-limit window starts over.

---

## Implemented Example

**File:** `redis_rate_limit_demo.py`

What the script demonstrates:

* Redis client initialization from `.env`
* building deterministic rate-limit keys
* atomic request counting with `INCR`
* window expiration using `EXPIRE`
* checking remaining TTL with `TTL`
* repeated simulated requests showing allow/deny behavior

The example uses:

* `limit = 3` requests
* `window = 10 seconds`

---

## Fixed Window Behavior

In a fixed window approach:

* all requests are counted inside one time window
* once the limit is exceeded, all further requests are denied
* when the window expires, the counter resets completely

This makes the algorithm:

* simple
* fast
* easy to reason about

But it also has known limitations (see below).

---

## Atomicity and Safety

Redis guarantees that `INCR` is **atomic**:

* concurrent requests cannot corrupt the counter
* all application instances see consistent state

This makes Redis suitable as a shared rate-limit store
for horizontally scaled services.

---

## Limitations of Fixed Window

This approach has known drawbacks:

* burst traffic at window boundaries is allowed
* two separate commands are used (`INCR` + `EXPIRE`)
* precision is coarse for short windows

These trade-offs are acceptable for many systems,
but more advanced strategies exist.

---

## Environment Variables

The script reads Redis connection parameters from `.env`:

* `REDIS_HOST` (default: `localhost`)
* `REDIS_PORT` (default: `6379`)
* `REDIS_DB` (default: `0`)
* `REDIS_PASSWORD` (optional)

---

## Running the Demo

1. Start Redis.
2. Run the script:

```bash
python redis_rate_limit_demo.py
```

Expected behavior:

* first requests are allowed
* once the limit is exceeded, requests are denied
* after TTL expiration, requests are allowed again

---

## Educational Focus

This module emphasizes:

* how rate limiting works using counters
* why TTL is essential for windowing
* how Redis acts as shared state
* how limits are enforced consistently across processes

The code favors clarity and observability over optimization.

---

## Position in the Course

This lesson completes the Redis block:

* caching — fast reads
* queues — async processing
* rate limiting — traffic control

Together, these patterns show Redis as a versatile
in-memory data structure server for distributed systems.
