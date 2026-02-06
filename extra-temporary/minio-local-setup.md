# MinIO Object Storage Setup (Docker)

## Purpose

This document describes how to run a **local MinIO object storage** using **Docker** for development and testing.

The setup is intentionally minimal:

* no persistent volumes,
* no docker-compose,
* no production hardening.

The goal is to provide a **simple and reproducible S3-compatible storage** that can be started and removed quickly during local development.

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

## MinIO Version

This setup uses the **official MinIO Docker image**.

The `latest` image is sufficient for local development and testing. If strict version pinning is required, it can be added later.

---

## Run MinIO Container

Execute the following commands to start a local MinIO instance:

```bash
docker pull minio/minio
```

```bash
docker run -d \
  --name agent-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER='minio' \
  -e MINIO_ROOT_PASSWORD='minio123' \
  minio/minio server /data --console-address ':9001'
```

### What this does

* Creates a container named `agent-minio`
* Exposes the S3 API on port `9000`
* Exposes the MinIO web console on port `9001`
* Sets root credentials:

  * User: `minio`
  * Password: `minio123`
* Uses `/data` as the internal storage directory
* Runs the container in detached mode

No volumes are attached. All data is ephemeral.

---

## Verify Container Status

Check that the container is running:

```bash
docker ps
```

You should see `agent-minio` with status `Up`.

---

## Access MinIO

### Web Console

Open the MinIO web interface in your browser:

```
http://localhost:9001
```

Login credentials:

* User: `minio`
* Password: `minio123`

---

### S3 API Endpoint

Use the following endpoint to connect from applications:

* Endpoint: `http://localhost:9000`
* Access Key: `minio`
* Secret Key: `minio123`

---

## Stop and Remove the Container

When the storage is no longer needed:

```bash
docker stop agent-minio
docker rm agent-minio
```

All stored objects will be removed together with the container.

---

## Notes

* This setup is **for local development only**.
* Credentials are intentionally simple and not secure.
* Data is not persisted between container restarts.
* For long-lived projects, volumes and access policies should be added separately.

This document focuses on clarity and predictability rather than production readiness.
