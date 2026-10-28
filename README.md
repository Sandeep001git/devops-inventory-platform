[![CI](https://github.com/Sandeep001git/devops-inventory-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Sandeep001git/devops-inventory-platform/actions/workflows/ci.yml)

# DevOps Platform

A portfolio project for building and operating a containerized inventory management API using practical DevOps workflows.

## Project Goals

- Build a REST API with Python and FastAPI.
- Use PostgreSQL for persistent data storage.
- Containerize the application and its dependencies with Docker.
- Automate quality checks with GitHub Actions.
- Document setup, testing, and operational procedures.

## Current Status

The project includes a working inventory API, PostgreSQL integration, database migrations, Docker Compose services, automated tests, and CI security checks.

The CI workflow includes Ruff linting, pytest, Bandit security analysis, and Trivy container vulnerability scanning. GitHub Actions dependencies are pinned to commit SHAs, and Dependabot is configured to propose dependency updates.

The application has been verified locally with Docker Compose, including API health and readiness checks, API container restarts, PostgreSQL restarts, and continued access to existing inventory records.

## Development Environment

- Ubuntu 24.04 LTS on WSL2
- Git
- Docker Desktop with WSL integration
- Python 3.12
- FastAPI
- PostgreSQL 17
- Docker Compose
- pytest
- Ruff
- Bandit
- Trivy
- GitHub Actions
- Dependabot

## Project Principles

- Prefer local development with no required cloud spending.
- Keep configuration and secrets out of version control.
- Verify changes with repeatable commands.
- Document failures, fixes, and operational decisions.
- Keep development and test databases separate.
- Use parameterized SQL queries to protect against SQL injection.
- Pin GitHub Actions to full commit SHAs.
- Preserve PostgreSQL data using a named Docker volume.
- Run automated checks before merging changes.

## API Endpoints

The API is available at `http://127.0.0.1:8000` when running locally.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Service information |
| GET | `/health` | API liveness check |
| GET | `/ready` | PostgreSQL readiness check |
| GET | `/items` | List inventory items |
| POST | `/items` | Create an inventory item |
| GET | `/items/{item_id}` | Retrieve one inventory item |
| PUT | `/items/{item_id}` | Replace an inventory item |
| PATCH | `/items/{item_id}` | Update selected inventory fields |
| DELETE | `/items/{item_id}` | Delete an inventory item |

Interactive API documentation is available at `/docs` while the API is running.

## Local Operations

Run the following commands from the repository root. They use standard Docker Compose syntax and explicitly load configuration from `.env.dev`; no custom shell alias is required.

### Start the services

Build the API image and start PostgreSQL and the API:

```bash
docker compose --env-file .env.dev up -d --build
```

### Check service status

```bash
docker compose --env-file .env.dev ps
```

Check that the services are running and that their health checks pass where configured.

### Check API health and readiness

```bash
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/ready
```

- `/health` checks whether the API responds.
- `/ready` checks whether the API can access PostgreSQL.

### View service logs

View recent API logs:

```bash
docker compose --env-file .env.dev logs --tail=100 api
```

View recent PostgreSQL logs:

```bash
docker compose --env-file .env.dev logs --tail=100 db
```

### Restart a service

Restart the API:

```bash
docker compose --env-file .env.dev restart api
```

Restart PostgreSQL:

```bash
docker compose --env-file .env.dev restart db
```

Restarting PostgreSQL temporarily interrupts database access while the service restarts.

### Run automated checks

Run the project's lint and test checks:

```bash
make check
```

The test command uses the dedicated `devops_inventory_test` database. Keep development data in `devops_inventory` separate from test data.

### API documentation

When the API is running, open Swagger UI in your browser:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Data persistence

PostgreSQL stores its data in the named Docker volume `postgres_data`. Restarting a service does not intentionally delete persisted database records.

**Important:** Do not run `docker compose --env-file .env.dev down -v` or remove the `postgres_data` volume unless you deliberately intend to delete the persisted database data.

### Local environment configuration

The `.env.dev` file contains local development configuration and must not be committed to version control.

If the repository provides an `.env.example` file, use it as a reference for the required environment variables. Keep real passwords, tokens, and other secrets out of the example file and Git history.