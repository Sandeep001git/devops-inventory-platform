# DevOps Platform

A portfolio project for building and operating a containerized inventory
management API using practical DevOps workflows.

## Project Goals

- Build a REST API with Python and FastAPI.
- Use PostgreSQL for persistent data storage.
- Containerize the application and its dependencies with Docker.
- Automate quality checks with GitHub Actions.
- Document setup, testing, and operational procedures.

## Current Status

Initial repository setup. Application implementation and automation are
planned and will be documented as they are completed and verified.

## Development Environment

- Ubuntu 24.04 LTS on WSL2
- Git
- Docker Desktop with WSL integration

## Project Principles

- Prefer local development with no required cloud spending.
- Keep configuration and secrets out of version control.
- Verify changes with repeatable commands.
- Document failures, fixes, and operational decisions.


## API Endpoints

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

Interactive API documentation is available at `/docs` while the development server is running.
