# Docker Usage Guide

This document describes how to build and run the TestizerFunnelEngine service in Docker.

Suitable for both local deployment and server deployment.

## 1. Requirements

Before starting, you need:

- Docker installed;
- `.env` file in the project root with correct settings:
  - MySQL (MODX) database access;
  - Brevo settings (API key, base URL, lists);
  - Application parameters (`APP_ENV`, `APP_DRY_RUN`, etc.).

The container uses the same environment variables as local Python execution.

## 2. Building Docker Image

From the project root:

```powershell
docker build -t testizer-funnel-engine .
```

After running this command, you will have an image named `testizer-funnel-engine` containing all project code and dependencies from `requirements.txt`.

## 3. Running the Main Task

The main task corresponds to the local command:

```powershell
python -m app.main
```

In Docker, it will look like this:

```powershell
docker run --rm --env-file .env testizer-funnel-engine
```

Important points:

* `--env-file .env` passes environment variables from the local `.env` file into the container;
* the container will connect to MySQL using `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_CHARSET` parameters.

If the database and Docker container are on the same machine, you may need to change `DB_HOST`. For example:

* use `host.docker.internal` instead of `127.0.0.1` (depends on environment and hosting).

## 4. Dry Run and Production Mode

The service can work in two modes:

* `APP_DRY_RUN=true`

  Does not actually send anything to Brevo, only makes requests, writes logs, and can be used to verify logic.

* `APP_DRY_RUN=false`

  Full production mode: contacts are sent to Brevo, funnel entries and purchases are recorded for real.

Examples:

Running in dry run:

```powershell
docker run --rm --env-file .env -e APP_DRY_RUN=true testizer-funnel-engine
```

Running in production mode:

```powershell
docker run --rm --env-file .env -e APP_DRY_RUN=false testizer-funnel-engine
```

If the `APP_DRY_RUN` variable is already specified in `.env`, you don't need to pass it via `-e`, and can manage the mode directly in `.env`.

## 5. Using Docker with Scheduling

There are two basic options.

### 5.1. Host-Side Scheduling

On the server, you can:

* configure cron (or a scheduler in the hosting panel) that runs a command like this every N minutes:

```bash
docker run --rm --env-file /path/to/.env testizer-funnel-engine
```

Each such run performs one full cycle:

* fetches candidates from MODX;
* sends contacts to Brevo;
* records funnel entry;
* syncs purchases and updates status.

Repeated runs are safe: the logic relies on the state of the `funnel_entries` table and does not duplicate data.

### 5.2. External Orchestrator

If the service will run in Kubernetes, Docker Swarm, or another orchestration system:

* use the same `testizer-funnel-engine` image;
* container startup command: `python -m app.main`;
* environment variables and schedule are set by the orchestrator.

## 6. Running Tests Inside Docker (Optional)

For additional verification, you can run tests directly in the container:

```powershell
docker run --rm testizer-funnel-engine python -m pytest
```

This is not required for production, but useful:

* for debugging;
* for manual verification before deployment;
* if the server doesn't have local Python but has Docker.

## 7. Quick Docker Checklist

1. Build the image:

   ```powershell
   docker build -t testizer-funnel-engine .
   ```

2. Test in dry run mode:

   ```powershell
   docker run --rm --env-file .env -e APP_DRY_RUN=true testizer-funnel-engine
   ```

3. After verification, switch to production mode:

   ```powershell
   docker run --rm --env-file .env -e APP_DRY_RUN=false testizer-funnel-engine
   ```

4. Connect the Docker command to the server schedule and run with the required frequency.

