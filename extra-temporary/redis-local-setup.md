# Redis Setup (Docker)

## Purpose

This document describes how to run a **local Redis instance** using **Docker** for development and testing purposes.

The setup is intentionally minimal and ephemeral:

* no persistent volumes,
* no authentication,
* no clustering or replication.

The goal is to provide a **fast, disposable in-memory datastore** suitable for local development scenarios such as caching, rate limiting, or event deduplication.

---

## Prerequisites

Before starting, ensure that:

* Docker Desktop is installed and running
* Docker CLI is available in your terminal

Verify Docker installation:

```bash
docker --version
```

---

## Redis Version

The setup uses the **official Redis Docker image**.

By default, the `latest` tag is used. For local development, this is acceptable, as Redis maintains strong backward compatibility.

If strict version pinning is required, the image tag can be adjusted explicitly.

---

## Run Redis Container

Start a local Redis instance with the following command:

```bash
docker run --name agent-redis \
  -p 6379:6379 \
  -d redis
```

### What this does

* Creates a container named `agent-redis`
* Exposes Redis on port `6379`
* Runs Redis in detached mode
* Uses in-memory storage only (no persistence)

All data will be lost when the container is stopped or removed.

---

## Verify Container Status

Check that the container is running:

```bash
docker ps
```

You should see `agent-redis` with status `Up`.

---

## Verify Redis Availability

To verify that Redis is accepting connections:

```bash
docker exec -it agent-redis redis-cli ping
```

Expected response:

```
PONG
```

---

## Connection Parameters

Use the following parameters to connect from an application (e.g. Python, local services):

* Host: `localhost`
* Port: `6379`

No password or authentication is configured.

---

## Stop and Remove the Container

When Redis is no longer needed:

```bash
docker stop agent-redis
docker rm agent-redis
```

All stored data will be removed together with the container.

---

## Notes

* This setup is intended for **local development only**.
* Redis persistence (RDB/AOF) is intentionally disabled.
* Authentication and network isolation are omitted for simplicity.
* For production or long-lived environments, additional configuration is required.

This document prioritizes clarity, predictability, and fast iteration over completeness.
