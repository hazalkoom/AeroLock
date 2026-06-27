# AeroLock

AeroLock is a real-time, distributed backend API engine that prevents double-booking of flight seats using a Redis distributed lock and a PostgreSQL ACID ledger.

## Core Features

- **Low-Latency Reads**: Serves flight search results from a Redis cache (cache-aside pattern) with low-latency reads.
- **Seat Lock Protection**: Acquires a distributed lock on a seat the instant a user requests it, preventing multiple users from holding the same seat simultaneously.
- **Idempotent Confirmations**: Confirms bookings with unique idempotency keys, ensuring that network retries or payment webhooks never create duplicate transactions.

---

## Directory Map

For a quick-start reference, see [context.md](file:///run/media/hazalkoom/FD16124010E85459/big project/AreoLock/aerolock/context.md). Below is the high-level repository layout:

- `gateway/` - FastAPI REST edge service which applies rate limiting, logging, and calls stubs over gRPC.
- `inventory-service/` - gRPC service managing booking locks and confirmations using Redis and PostgreSQL.
- `search-service/` - gRPC service managing read-only cached searches in front of PostgreSQL.
- `shared/` - Generated Python protobuf code and common helper packages.
- `proto/` - Protobuf contract definitions (`common.proto`, `inventory.proto`, `search.proto`).
- `tests/` - Contains E2E tests (`tests/e2e`), performance harness, and security tests.

---

## Current Status & Verification

All core write path (booking, locking, concurrency, idempotency) and read path (cached searches, validations) have been aligned with gRPC/Postgres schemas and verified:

- **E2E Test Suite**: `8/8` E2E tests passing. Checks booking flow, concurrent lock contention (10 users, 1 seat), idempotent retries, invalid tokens, invalid airport parameters, and seat booking exclusivity.
- **Unit Test Coverage**: `18/18` unit tests passing across all three services.
- **Seeding & Reset**: Integrated Redis lock clear (`FLUSHALL`) and Postgres seeding script (`inventory-service/db/seed1.py`) for reproducible, CI/CD-ready testing.

For full implementation logs and findings, refer to [report.md](file:///run/media/hazalkoom/FD16124010E85459/big project/AreoLock/aerolock/report.md).

---

## What is Still Not Done Yet

To take the AeroLock system from the current development phase to a production-ready, release-grade state, the following gaps need to be addressed:

### 1. Deployment & Infrastructure
- **`docker-compose.override.yml`**: Currently empty. Needs local volume mounts mapped into container paths to allow live-reloading of Python code during development without requiring container rebuilds.
- **Kubernetes Manifests (`k8s/`)**: The `base/` directory and environment overlays (`overlays/dev/` and `overlays/prod/`) are currently empty. Real Kubernetes manifests (Deployments, Services, ConfigMaps, Secrets, and Ingresses) need to be written.
- **Script Hardening (`scripts/`)**: Operational wrappers (such as `scripts/deploy_k8s.sh`) are placeholder scaffolds that need to be expanded with parameter checks, environment setups, and sanity validation.
- **Image Publishing Strategy**: The docker-compose configuration builds containers from local source. A real CI/CD pipeline needs to be added to build, tag, and publish production-ready docker images.

### 2. Testing Expansion
- **Performance Testing (`tests/performance/`)**: The locust/k6 harness files are empty. Load/soak test cases need to be written to simulate high concurrency booking spikes and measure lock acquisition latencies.
- **Security Testing (`tests/security/`)**: Security test cases (OWASP API checks, token spoofing, bypass audits) are empty placeholders that need real scenario implementations.

### 3. Runtime & Code Polish
- **Graceful Shutdown Warnings**: gRPC services emit shutdown warning alerts on `Ctrl+C` because asynchronous server teardown runs after the asyncio loop closes. Teardown logic needs to be aligned.
- **API Documentation Drift**: Docs contain minor drift regarding lock TTLs, rate-limiting semantics, and some API path parameters.
- **FastAPI OpenAPI Cleanup**: Stacked route decorators on the Gateway routes result in duplicate FastAPI OpenAPI operation IDs, which should be normalized.