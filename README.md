# AeroLock

AeroLock is a high-performance, real-time distributed flight booking engine designed to prevent double-booking of flight seats using a Redis distributed locking mechanism and a PostgreSQL ACID ledger. It features extremely low-latency reads via Redis cache-aside caching, bullet-proof idempotent booking confirmations, and real-time updates via WebSockets.

🌐 **Deployed Version:** [http://YOUR_AZURE_VM_IP](http://YOUR_AZURE_VM_IP) *(Replace with your Azure VM Public IP once deployed)*

🚀 **Performance Benchmarks:** Our local development infrastructure sustains up to **800 concurrent users** and **over 300+ Requests Per Second (RPS)** with **0% failure rate** and a 95th percentile latency of under 350ms.

---

## 🏗️ Architecture Overview
AeroLock is built using a modern, containerized microservices architecture:
*   **Gateway Service (`gateway/`)**: A FastAPI edge service. Exposes public REST endpoints, applies rate limiting, handles live WebSocket events, and routes gRPC commands to internal services.
*   **Inventory Service (`inventory-service/`)**: Manages flight database bookings and handles concurrent seat locking using Redis-based mutual exclusion (Redlock).
*   **Search Service (`search-service/`)**: Exposes read-only flight and seat search queries over gRPC with a Redis cache-aside layer.
*   **Shared Library (`shared/`)**: Holds protobuf contract files and automatically generated Python gRPC stubs.
*   **Infrastructure (`k8s/`)**: Fully production-ready Kubernetes manifests including ConfigMaps, Secrets, StatefulSets for databases, Deployments with auto-scaling replicas, and an Ingress controller.

---

## ⚡ Running the Project Locally

### Prerequisites
*   Docker and Docker Compose installed.

### Start the Stack
To boot the database, cache, and all microservices together:
```bash
./scripts/run_local.sh
```
This script will build the Docker images locally and launch the containers.

### Access the App
*   **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Gateway Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Running the Test Suites
AeroLock comes with a robust test suite spanning unit, E2E, security, and performance test suites:
*   **E2E Tests**: `cd tests && poetry run pytest e2e/`
*   **Security Suite**: `cd tests && poetry run pytest security/`
*   **Load Testing**: `cd tests && poetry run locust -f performance/locustfile.py`

---

## 🚢 Cloud Deployment (Azure VM)
The project is configured for continuous delivery using GitHub Actions and Kubernetes.
*   **CD Pipeline**: Every merge to `main` builds and pushes the microservices to the GitHub Container Registry (`ghcr.io/hazalkoom/aerolock-*`).
*   **Production Host**: Deployed to an **Azure Virtual Machine** running Ubuntu 24.04 LTS (Standard_B2als_v2, 2 vCPUs, 4 GiB RAM) in the Sweden Central region.

*Detailed deployment setup and guides can be found in [docs/Deployment.md](docs/Deployment.md).*