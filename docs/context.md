# AeroLock Context

This file is the fast-start map for the AeroLock repository. Read this first to understand the project, the folder layout, the current implementation status, and what still needs work.

## What This Project Is

AeroLock is a microservices-based flight booking backend.

It is built around three runtime services plus shared protobuf code:

- `gateway/` is the FastAPI edge service. It exposes REST endpoints, applies rate limiting, logs requests, and calls the backend services over gRPC.
- `inventory-service/` manages booking locks and confirmed bookings using Redis and PostgreSQL.
- `search-service/` exposes read-only flight search over gRPC and uses Redis cache-aside in front of PostgreSQL.
- `shared/` contains shared Python protobuf/gRPC code generation output and common support modules.
- `proto/` contains the source `.proto` contracts used to generate the shared Python stubs.

The system is meant to prevent double-booking, return search results quickly, and keep booking confirmation idempotent.

## Repository Layout

Root-level files and folders:

- `docker-compose.yml` - local full-stack app orchestration.
- `docker-compose.override.yml` - currently empty; intended for developer overrides.
- `README.md` - project overview and links.
- `report.md` - rolling project status and implementation notes.
- `context.md` - this fast-start summary.
- `LICENSE` - license file.
- `Makefile` - root task helper.
- `docs/` - requirements, architecture, API, deployment, testing, and learning docs.
- `gateway/` - FastAPI gateway service.
- `inventory-service/` - booking/inventory gRPC service.
- `search-service/` - search gRPC service.
- `shared/` - shared protobuf-generated Python package.
- `proto/` - source protobuf definitions.
- `scripts/` - developer and deployment helper scripts.
- `k8s/` - Kubernetes base and overlays.
- `tests/` - root e2e, performance, and security test assets.

## Folder Map

### `proto/`

Source protobuf contracts:

- `common.proto` - shared messages such as `Flight`, `Seat`, and `ErrorResponse`.
- `inventory.proto` - inventory service RPCs and request/response types.
- `search.proto` - search service RPCs and request/response types.

### `shared/`

Shared Python package used by the services:

- `pyproject.toml` - package metadata and shared Python dependency declarations.
- `aerolock_common/` - generated/common Python package.
- `aerolock_common/generated/` - generated protobuf Python modules.

Important generated files under `shared/aerolock_common/generated/`:

- `common_pb2.py` and `common_pb2.pyi`
- `common_pb2_grpc.py`
- `inventory_pb2.py` and `inventory_pb2.pyi`
- `inventory_pb2_grpc.py`
- `search_pb2.py` and `search_pb2.pyi`
- `search_pb2_grpc.py`
- `__init__.py`

### `gateway/`

FastAPI REST-to-gRPC gateway:

- `Dockerfile` - container image definition.
- `pyproject.toml` - gateway Python dependencies.
- `pytest.ini` - test config.
- `requirements.txt` - currently present but empty.
- `app/main.py` - FastAPI app entrypoint, rate limiting, logging, route registration.
- `app/api/booking.py` - booking routes.
- `app/api/search.py` - search routes.
- `app/clients/inventory_client.py` - gRPC client for inventory service.
- `app/clients/search_client.py` - gRPC client for search service.
- `app/core/config.py` - gateway settings.
- `app/core/logging.py` - structured logging.
- `app/middleware/rate_limit.py` - SlowAPI setup.
- `app/schemas/booking.py` - booking request/response schemas.
- `tests/unit/` - gateway unit tests.

### `inventory-service/`

Booking/inventory gRPC service:

- `Dockerfile` - container image definition.
- `pyproject.toml` - inventory Python dependencies.
- `pytest.ini` - test config.
- `requirements.txt` - currently present but empty.
- `app/main.py` - gRPC server entrypoint.
- `app/services/inventory_service.py` - gRPC service implementation.
- `app/core/config.py` - inventory settings.
- `app/core/logging.py` - structured logging.
- `app/db/session.py` - SQLAlchemy async session setup.
- `app/db/models.py` - SQLAlchemy models.
- `app/db/repository.py` - DB repository logic.
- `app/lock/redis_lock.py` - Redis lock manager.
- `db/schema.sql` - PostgreSQL schema.
- `db/seed.py` and `db/seed1.py` - database seed scripts.
- `tests/unit/` - inventory unit tests.
- `test_client.py` - local service test client.

### `search-service/`

Search gRPC service:

- `Dockerfile` - container image definition.
- `pyproject.toml` - search Python dependencies.
- `pytest.ini` - test config.
- `requirements.txt` - currently present but empty.
- `app/main.py` - gRPC server entrypoint.
- `app/server.py` - search gRPC service implementation.
- `app/cache.py` - Redis cache manager.
- `app/core/config.py` - search settings.
- `app/core/logging.py` - structured logging.
- `app/db/session.py` - SQLAlchemy async session setup.
- `app/db/repository.py` - search SQL queries.
- `app/db/seed1.py` - search seed script.
- `tests/unit/` - search unit tests.
- `test_client.py` - local service test client.

### `scripts/`

Developer/deployment helpers:

- `generate_protos.sh` - regenerates protobuf Python code into `shared/aerolock_common/generated/`.
- `run_local.sh` - starts the local Docker Compose stack.
- `run_e2e_tests.sh` - runs e2e tests through Poetry.
- `run_security_tests.sh` - runs security tests through Poetry.
- `run_performance_tests.sh` - placeholder runner for performance tooling.
- `deploy_k8s.sh` - placeholder Kubernetes deploy wrapper.

### `k8s/`

Kubernetes deployment tree:

- `base/` - currently empty manifests intended to define the deployable baseline.
- `overlays/dev/` - currently empty developer overlay.
- `overlays/prod/` - currently empty production overlay.

### `tests/`

Root test assets:

- `e2e/` - end-to-end tests. Several files exist but are still empty placeholders.
- `performance/` - performance test harnesses such as `k6` and `locust`, currently mostly empty scaffolds.
- `security/` - security-focused tests and configs, currently mostly empty scaffolds.

## Current Architecture Summary

Request flow:

1. Client calls the FastAPI gateway.
2. Gateway performs request logging and rate limiting.
3. Gateway calls search or inventory over gRPC.
4. Search reads from Redis first and falls back to PostgreSQL.
5. Inventory uses Redis locks and PostgreSQL bookings to prevent double-booking.
6. Shared protobuf types live in `proto/` and are consumed by all services through `shared/`.

## Current Working State

What is already working or largely in place:

- The protobuf contract includes `Flight.available_seats`.
- The search repository query matches the shared PostgreSQL schema.
- The generated protobuf import resolution bug was fixed by making the generated modules package-relative and removing the generated `sys.path` mutation.
- The stale `available_seats` runtime issue was traced to an old installed package, not to the `.proto` source.
- The three service Dockerfiles now build the app images and install runtime deps with `pip` plus editable `shared/`.
- `docker-compose.yml` now runs Postgres, Redis, gateway, inventory-service, and search-service together.
- The local stack can boot successfully.
- Fixed Docker Compose networking issue where `gateway` could not connect to `search-service` (it was trying to connect to `localhost` instead of the service name).
- Optimized Dockerfiles by removing `build-essential` after use to reduce image size.
- Refactored `gateway` to read service URLs directly from environment variables for better reliability in containerized environments.

## Current Gaps / Not Finished Yet

Important remaining work:

- `docker-compose.override.yml` is still empty.
- `k8s/base` and both overlays are still empty.
- The operational scripts are wrappers only and still need hardening.
- The seed scripts have been fully reviewed, aligned, and fixed.
- Documentation still has drift in API paths, lock TTL wording, and rate-limit wording.
- The gateway OpenAPI shows duplicate operation IDs from stacked decorators, which should be cleaned up.

## How To Run Locally

- Start the stack with `scripts/run_local.sh`.
- Open Swagger at `http://localhost:8000/docs`.
- Gateway health is at `http://localhost:8000/health`.
- Search and booking are exposed under `/api/v1/search` and `/api/v1/booking` on the gateway.

## Useful Notes For Other Models

- Treat `report.md` as the live project status log.
- Treat this file as the quick-start context map.
- The repository is in active development, not finished product state.
- The most important current task is to finish deployment and test scaffolding without reintroducing the protobuf import bug.