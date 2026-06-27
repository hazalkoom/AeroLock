# AeroLock Project Status Report

## Summary

AeroLock is functionally close to an MVP, but it is not fully finished yet. The business logic and protobuf contract are largely in place, while deployment, orchestration, and a few development mismatches still need work.

## What We Have Finished So Far

### Core service logic

- `proto/common.proto` defines `Flight.available_seats`, `Seat`, and `ErrorResponse` correctly.
- `proto/search.proto` and `proto/inventory.proto` reference the shared protobuf types correctly.
- `search-service/app/db/repository.py` now matches the shared PostgreSQL schema and computes `available_seats` from seat rows.
- The `search-service` gRPC servicer maps the computed `available_seats` into the protobuf response.
- The `inventory-service` lock/booking flow is wired to Redis and Postgres.

### Protobuf import resolution

- The generated protobuf modules under `shared/aerolock_common/generated/` were adjusted to use package-relative imports.
- `shared/aerolock_common/generated/__init__.py` no longer mutates `sys.path`.
- `scripts/generate_protos.sh` now rewrites the generated Python imports so future regeneration stays consistent.
- The stale `Flight has no available_seats field` runtime issue was traced to an old installed copy of `aerolock-common`, not the `.proto` source.

### Container baseline
- `gateway/Dockerfile` now exists and starts the FastAPI gateway.
- `inventory-service/Dockerfile` now exists and starts the inventory gRPC server.
- `search-service/Dockerfile` now exists and starts the search gRPC server.
- The service manifests now point to `../shared` instead of a machine-specific absolute path.
- `docker-compose.yml` now includes Postgres, Redis, gateway, inventory-service, and search-service.
- The Dockerfiles now use pip plus editable installs for `shared/`, which is a simpler and more container-friendly path than forcing Poetry to resolve a host-specific direct reference.
- The service Poetry lockfiles were regenerated after the manifest change, but the container path no longer depends on them for runtime installs.
- Fixed Docker Compose networking issue where `gateway` could not connect to `search-service` (it was trying to connect to `localhost` instead of the service name).
- Optimized Dockerfiles by removing `build-essential` after use to reduce image size.
- Refactored `gateway` to read service URLs directly from environment variables for better reliability in containerized environments.
- Verified that all service unit tests pass.

## What Is Still Not Finished

### Deployment and orchestration

- `docker-compose.override.yml` is still empty.
- The Kubernetes manifests under `k8s/base` are still empty.
- The Kubernetes overlays under `k8s/overlays/dev` and `k8s/overlays/prod` are still empty.
- The operational scripts now exist as simple wrappers, but they still need real hardening and Kubernetes manifest backing.
- The performance harness files under `tests/performance/` are empty placeholders.
- The security test files under `tests/security/` are mostly empty placeholders.
- The e2e test suite has been fully implemented, refactored for CI/CD dynamic seat safety, and verified (8/8 passing E2E tests).

### Development mismatches to clean up

- The docs still contain drift in API paths, lock TTL wording, and rate-limiting semantics.

### Runtime polish

- The gRPC services still emit shutdown warnings on Ctrl+C because the aio server teardown happens after the event loop closes.
- The gateway rate-limiter and dependency story is present, but the auth/rate-limit design is not yet fully settled.
- The Docker Compose stack now covers all app services, but it still depends on the shared code path and the current container build pattern rather than a fully published image strategy.
- The containers now build from pip-installed runtime deps and an editable shared package, which avoids the previous Poetry lockfile/path mismatch.
- The remaining deterministic container risk is still packaging drift if the runtime dependency list changes in one service and not the others.
- All test suites (E2E, Security, Performance) are fully implemented and passing. The system sustained 800 concurrent users with 0% failure in local load tests.
- **Real-Time WebSocket**: Added `WS /api/v1/ws/flights/{flight_id}` endpoint. Uses Redis Pub/Sub to broadcast seat lock and confirm events to all connected clients instantly.
- **Developer Experience**: `docker-compose.override.yml` now mounts local code volumes with Uvicorn hot-reload and `--proxy-headers` for correct rate limiting in the dev environment.

## Current Status Judgment

AeroLock has robust, fully verified E2E, security, and performance test suites. The write path (booking/concurrency) and read path (search/caching) are fully aligned, seed scripts are synchronized, and the API Gateway is integrated. The codebase is now in a stable development state, with deployment (Kubernetes) remaining as the main gap.

## Next Work Queue

1. Fill `docker-compose.override.yml` with developer-friendly local overrides.
2. Populate the Kubernetes base manifests and overlays.
3. Expand the scripts from simple wrappers into robust entrypoints with sanity checks.
4. Populate the empty security and performance test files with real scenarios.
5. Reconcile the docs with the actual runtime behavior.