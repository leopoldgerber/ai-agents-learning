# Practice: Agent Data Repository (3.2.3.1)

## About This Lesson

This lesson puts several previously learned concepts together in a single practical example:

* PostgreSQL as the **source of truth** for structured data
* Redis as an **in-memory cache** for fast reads
* a **Repository** layer that encapsulates data access
* a **Service** layer that contains business rules
* an **Orchestrator** script that wires everything together

The goal is to build a small but realistic architecture slice that can be reused in agent systems.

---

## Why a Repository Layer

When a system uses multiple storage layers (Postgres + Redis), it becomes easy to:

* duplicate SQL logic across the codebase,
* forget cache invalidation,
* mix business rules with storage details,
* make testing harder.

A repository solves this by providing a stable CRUD API and hiding:

* SQL queries,
* Redis key conventions,
* caching strategy and TTL,
* cache invalidation rules.

The service layer can then focus on business decisions.

---

## Layer Responsibilities

### Repository

The repository is responsible for:

* reading and writing agent data
* implementing the cache-aside pattern for reads
* invalidating cache on updates/deletes
* serializing data for Redis

It should **not** contain business rules.

### Service Layer

The service layer is responsible for:

* validating inputs
* applying business constraints (limits, policies)
* producing service-level responses
* orchestrating multiple repository calls when needed

It should not directly talk to Redis.

### Orchestrator

The orchestrator is responsible for:

* loading configuration from `.env`
* initializing dependencies
* calling service functions to demonstrate behavior

It is a simple “runner” that makes the architecture visible.

---

## Implemented Files

### `agent_repository.py`

Contains the repository implementation from the lesson example:

* `get_agent` uses cache-aside:

  1. check Redis
  2. fallback to Postgres
  3. cache the result with TTL
* `update_agent` and `delete_agent` invalidate Redis keys

This demonstrates the core caching mechanics in a single place.

---

### `agent_service.py`

Contains business logic that is intentionally separated from data access.

Included rules in this lesson:

* minimal payload validation (name/email)
* an example limit: max N agents per email
* consistent service responses (ok/error)

The service uses the repository as a black box.

---

### `orchestrator.py`

Demonstrates how the layers work together:

1. prepares the `agents` table
2. initializes repository and service
3. runs a flow:

   * create agent
   * read twice (cache hit on second read)
   * update (cache invalidation)
   * read again
   * delete (cache removal)

This makes cache behavior observable without building a full API server.

---

## Environment Variables

The orchestrator reads connection settings from `.env`.

### PostgreSQL

* `DB_NAME` (default: `agent`)
* `DB_USER` (default: `agent`)
* `DB_PASSWORD` (default: `agent`)
* `DB_HOST` (default: `localhost`)
* `DB_PORT` (default: `5432`)

### Redis

* `REDIS_HOST` (default: `localhost`)
* `REDIS_PORT` (default: `6379`)
* `REDIS_DB` (default: `0`)
* `REDIS_PASSWORD` (optional)

---

## Running the Demo

1. Ensure Postgres and Redis are running.
2. Install dependencies:

```bash
pip install psycopg2 redis python-dotenv
```

3. Run the orchestrator:

```bash
python orchestrator.py
```

Expected behavior:

* first read hits Postgres and populates cache
* second read returns from Redis
* update invalidates cache
* delete removes the cached entry

---

## Educational Focus

This lesson emphasizes:

* separation of concerns between service and repository
* using Redis to accelerate reads without losing Postgres correctness
* where cache invalidation belongs
* how to keep code maintainable when using multiple storage systems

It is a minimal foundation that can be extended toward production designs.
