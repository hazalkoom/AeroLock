# AeroLock

AeroLock is a high-performance, real-time distributed flight booking engine designed to prevent double-booking of flight seats using a Redis distributed locking mechanism and a PostgreSQL ACID ledger. It features extremely low-latency reads via Redis cache-aside caching, bullet-proof idempotent booking confirmations, and real-time updates via WebSockets.

🌐 **Live Deployed Version:** [http://aerolock-mohamed-ahmed.duckdns.org/docs](http://aerolock-mohamed-ahmed.duckdns.org/docs)

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

## 🚀 How We Deployed the Project (Azure & Kubernetes)

The application has been deployed to a production-grade cloud environment using the following steps:

1.  **Virtual Machine Provisioning**: Set up an **Azure Virtual Machine** running Ubuntu 24.04 LTS (`Standard_B2als_v2` with 2 vCPUs and 4 GiB of RAM) located in the Sweden Central region.
2.  **Container Registry**: Configured a GitHub Actions workflow (`docker-publish.yml`) that automatically builds Docker images for all three microservices and pushes them to the **GitHub Container Registry (GHCR)** on every merge to `main`.
3.  **Kubernetes Orchestration**: Installed **K3s** (a lightweight production-ready Kubernetes engine) on the Azure VM.
4.  **Declarative Manifests**: Applied Kubernetes resource definitions located in `k8s/`:
    *   `configmap.yaml` and `secrets.yaml` for environment variables and secure credentials.
    *   `postgres.yaml` and `redis.yaml` `StatefulSets` with persistent volume claims to ensure database durability.
    *   `gateway.yaml`, `inventory-service.yaml`, and `search-service.yaml` `Deployments` running replica pods pulling from GHCR.
    *   `ingress.yaml` to route public HTTP and WebSocket traffic through K3s Ingress directly to the Gateway.
5.  **Domain Association**: Linked a free dynamic domain (`aerolock-mohamed-ahmed.duckdns.org`) to the VM's public IP (`20.91.215.170`).

---

## 🧪 How to Test the Live Application

You can test the entire API flow directly from the live Swagger UI:

1.  **Open the App**: Navigate to [http://aerolock-mohamed-ahmed.duckdns.org/docs](http://aerolock-mohamed-ahmed.duckdns.org/docs).
2.  **Search for Flights**:
    *   Expand the `GET /api/v1/search` endpoint.
    *   Click **Try it out**.
    *   Enter `CAI` (Cairo) for the `origin` and `DXB` (Dubai) for the `destination`.
    *   Click **Execute**. You will see the flight details returned from PostgreSQL via the Search Service.
    *   Copy the `"flight_id"` (e.g. `c3c577d6-bb82-4cc3-a112-c9435f3ff0a1`) and a `"seat_number"` (e.g. `1A`) from the response.
3.  **Lock a Seat**:
    *   Expand the `POST /api/v1/booking/lock` endpoint.
    *   Click **Try it out** and paste the `flight_id` and `seat_number` into the request body.
    *   Click **Execute**. This obtains a Redis-backed mutual exclusion lock on that seat.
4.  **Confirm the Booking**:
    *   Expand `POST /api/v1/booking/confirm`.
    *   Execute the request using the flight ID, seat number, and an `idempotency_key` (any random string) to permanently commit the booking to the PostgreSQL ACID ledger.

---

## ⚡ Running the Project Locally (Alternative)

### Prerequisites
*   Docker and Docker Compose installed.

### Start the Stack
To boot the database, cache, and all microservices together locally:
```bash
./scripts/run_local.sh
```

### Access the App Locally
*   **Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Gateway Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Running the Test Suites
*   **E2E Tests**: `cd tests && poetry run pytest e2e/`
*   **Security Suite**: `cd tests && poetry run pytest security/`
*   **Load Testing**: `cd tests && poetry run locust -f performance/locustfile.py`