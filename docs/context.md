# AeroLock Context

This file is the fast-start map for the AeroLock repository. Read this first to understand the project, the folder layout, the current implementation status, and deployment strategies.

## What This Project Is

AeroLock is a microservices-based flight booking backend. It prevents double-booking, returns search results instantly using Redis caching, and provides real-time WebSockets.

It is built around three runtime services plus shared protobuf code:
- `gateway/`: FastAPI edge service. Exposes REST endpoints, applies rate limiting, handles WebSockets (using Redis Pub/Sub), and calls backend services over gRPC.
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
- `gateway/`, `inventory-service/`, `search-service/` - The core microservices.
- `shared/` & `proto/` - Shared gRPC communication contracts.
- `k8s/` - Production Kubernetes deployment manifests.
- `.github/workflows/` - CI/CD pipelines.

## CI/CD Pipeline (GitHub Actions)

AeroLock features a fully automated, production-grade CI/CD pipeline:
1. **Testing**: `gateway-ci.yml`, `inventory-ci.yml`, `search-ci.yml` run `pytest` and upload code coverage to Codecov. End-to-End tests (`e2e.yml`) and Security tests (`security.yml`) run on Docker-compose stacks.
2. **Code Quality**: `code-quality.yml` runs `ruff` (linting/formatting), `bandit` (SAST), and `safety` (dependency audit).
3. **Advanced Security**: `codeql.yml` runs semantic code analysis, and `secret-scan.yml` uses TruffleHog to ensure no passwords/keys are leaked.
4. **Dependabot**: `.github/dependabot.yml` automatically groups and tests dependency updates.
5. **Continuous Deployment (CD)**: `docker-publish.yml` automatically builds Docker images for all three services and pushes them to the GitHub Container Registry (GHCR) on every merge to `main`.

## Kubernetes (Production) Deployment

The project has transitioned from local `docker-compose` to production Kubernetes.
- `k8s/config/` - ConfigMaps and Secrets.
- `k8s/databases/` - StatefulSets for Postgres and Redis.
- `k8s/services/` - Deployments for the microservices referencing the GHCR Docker images.
- `k8s/ingress/` - NGINX Ingress rules for routing public traffic to the gateway.

## How To Run Locally

- Start the stack with `docker compose up -d --build`.
- Open Swagger at `http://localhost:8000/docs`.
- Gateway health is at `http://localhost:8000/health`.

## Useful Notes For Online LLMs
If you are an AI assistant helping the user deploy or debug this project, please note:
1. **Docker Images**: Are hosted on GitHub Container Registry (`ghcr.io`). The CI pipeline automatically pushes them.
2. **Kubernetes**: To deploy, the user simply needs a working K8s cluster (like K3s on Oracle Cloud or Minikube) and must run `kubectl apply -f k8s/config/`, then `databases/`, then `services/`, then `ingress/`.
3. **WebSockets**: Implemented in `gateway/app/api/websocket.py` using Redis Pub/Sub. Do not attempt to rebuild this feature.
4. **Environment Variables**: Managed via `k8s/config/configmap.yaml` and `k8s/config/secrets.yaml`.