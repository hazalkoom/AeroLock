# AeroLock Context

This file is the fast-start map for the AeroLock repository. Read this first to understand the project, the folder layout, the current implementation status, and deployment strategies.

## What This Project Is

AeroLock is a microservices-based flight booking backend. It prevents double-booking, returns search results instantly using Redis caching, provides real-time WebSockets, and enforces secure client authentication.

It is built around four runtime services plus shared protobuf code:
- `gateway/`: FastAPI edge service. Exposes REST endpoints (including secure authentication), applies rate limiting, handles live WebSocket events, and routes gRPC commands to internal services. Confirms token authenticity using RS256 public key.
- `user-service/`: Manages user credentials, native `bcrypt` password hashing, registration, and authentication over gRPC. Signs JWTs using RS256 private key.
- `inventory-service/`: Manages booking locks and confirmed bookings using Redis locks and PostgreSQL.
- `search-service/`: Exposes read-only flight search over gRPC and uses Redis cache-aside in front of PostgreSQL.
- `shared/`: Shared Python protobuf/gRPC code and common utilities.
- `proto/`: Source `.proto` contracts used to generate the shared Python stubs.

## Repository Layout

Root-level files and folders:
- `docker-compose.yml` - Local full-stack app orchestration for testing.
- `README.md` - Project overview and links.
- `report.md` - Production Readiness Report (Deployment options).
- `docs/` - Requirements, architecture, API, deployment, testing, and context docs.
- `gateway/`, `user-service/`, `inventory-service/`, `search-service/` - The core microservices.
- `shared/` & `proto/` - Shared gRPC communication contracts.
- `k8s/` - Production Kubernetes deployment manifests.
- `.github/workflows/` - CI/CD pipelines.

## Security & Authentication (Phase 1)

AeroLock implements enterprise-grade asymmetric authorization:
*   **Asymmetric RS256 JWTs**: The private key is held exclusively in `user-service` to sign tokens during `/login`. The public key is distributed to the `gateway` to verify token signatures mathematically, eliminating key sharing.
*   **Password Hashing**: Employs raw, native `bcrypt` for secure hashing and salting (no legacy wrappers).
*   **Access Control**: The `/api/v1/booking/confirm` REST endpoint is guarded via a gateway dependency (`get_current_user`) requiring a valid Bearer token.

## How To Run Locally

- Start the stack with `docker compose up -d --build`.
- Open Swagger at `http://localhost:8000/docs`.
- Gateway health is at `http://localhost:8000/health`.

## Useful Notes For Online LLMs
If you are an AI assistant helping the user deploy or debug this project, please note:
1. **Docker Images**: Are hosted on GitHub Container Registry (`ghcr.io`). The CI pipeline automatically pushes them.
2. **WebSockets**: Implemented in `gateway/app/api/websocket.py` using Redis Pub/Sub. Do not attempt to rebuild this feature.
3. **User Auth**: Built on RS256. Do not commit or push the private cryptographic key files (`jwt_private.pem`) to the repository. Keep them in environment variables or volume mounts.