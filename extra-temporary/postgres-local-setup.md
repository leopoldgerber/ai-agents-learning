# PostgreSQL Database Setup (Docker)

## Purpose

This document describes how to run a **local PostgreSQL database** using **Docker** for development and experimentation.

The setup is intentionally minimal:

* no persistent volumes,
* no docker-compose,
* no production hardening.

The goal is to provide a **clean, reproducible database environment** that can be created and destroyed quickly during local development.

---

## Prerequisites

Before starting, make sure you have:

* Docker Desktop installed and running
* Docker CLI available in your terminal

You can verify Docker with:

```bash
docker --version
```

---

## PostgreSQL Version

This setup uses **PostgreSQL 15**.

The version is explicitly pinned to avoid:

* driver incompatibilities,
* unexpected behavior changes between major versions.

---

## Run PostgreSQL Container

Execute the following command to start a local PostgreSQL instance:

```bash
docker run --name agent-postgres \
  -e POSTGRES_USER='agent' \
  -e POSTGRES_PASSWORD='agent' \
  -e POSTGRES_DB='agent' \
  -p 5432:5432 \
  -d postgres:15
```

### What this does

* Creates a container named `agent-postgres`
* Creates a database named `agent`
* Sets username and password to `agent`
* Exposes PostgreSQL on port `5432`
* Runs the container in detached mode

No volumes are attached. All data is ephemeral.

---

## Verify Container Status

Check that the container is running:

```bash
docker ps
```

You should see `agent-postgres` with status `Up`.

---

## Verify PostgreSQL Version

To confirm the running PostgreSQL version:

```bash
docker exec -it agent-postgres psql -U agent -d agent -c 'SELECT version();'
```

---

## Connection Parameters

Use the following parameters to connect from a client (e.g. Python, HeidiSQL):

* Host: `localhost`
* Port: `5432`
* Database: `agent`
* User: `agent`
* Password: `agent`

---

## Stop and Remove the Container

When the database is no longer needed:

```bash
docker stop agent-postgres
docker rm agent-postgres
```

All data will be removed together with the container.

---

## Notes

* This setup is **for local development only**.
* Credentials are intentionally simple and not secure.
* For long-lived projects, persistence and configuration management should be added separately.

This document focuses on clarity and predictability rather than completeness.
