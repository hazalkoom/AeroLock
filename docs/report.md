# AeroLock Project Status Report

## Summary

AeroLock is a fully completed, production-ready, high-performance flight booking backend MVP. It features robust gRPC microservices (including secure authentication), Redis caching and locking, automated CI/CD pipelines, and is successfully deployed to a live Azure Kubernetes (K3s) cluster.

---

## What We Have Finished

### 1. Core Service Logic & Protocols
*   **Gateway Service (`gateway/`)**: A FastAPI edge service. Exposes public REST endpoints, applies rate limiting, handles live WebSocket events, verifies RS256 JWT tokens using public keys, and routes gRPC commands.
*   **User Service (`user-service/`)** [NEW]: A Python gRPC microservice managing user registration and authentication, native `bcrypt` password hashing, and token signing using a secure RS256 private key.
*   **Inventory Service (`inventory-service/`)**: Manages flight database bookings and handles concurrent seat locking using Redis-backed mutual exclusion (Redlock).
*   **Search Service (`search-service/`)**: Exposes read-only flight and seat search queries over gRPC with a Redis cache-aside layer (60s TTL).
*   **Shared Library (`shared/`)**: Holds protobuf contract files and automatically generated Python gRPC stubs.
*   **Real-Time Synchronization**: Added `WS /api/v1/ws/flights/{flight_id}` endpoint using Redis Pub/Sub to broadcast seat lock and confirm events to all connected clients instantly.

### 2. Phase 1 Security & Database Schema Upgrades
*   **Asymmetric Cryptography**: Implemented RS256 JWT tokens (private key is stored safely on user-service for signing, gateway holds public key for stateless signature mathematical validation).
*   **Bouncer Middleware**: Locked down `/api/v1/booking/confirm` using the gateway `get_current_user` dependency.
*   **Database Upgrades**: Executed schema modifications to include:
    *   `users` table storing salted native bcrypt hashed passwords.
    *   `passengers` table mapping bookings to passengers.
    *   `pnr` (Passenger Name Record) and `total_price` in the bookings table.

### 3. Comprehensive Test Suites (`tests/`)
AeroLock has robust, fully verified test suites:
*   **E2E Tests (`tests/e2e/`)**: Runs integration tests covering search, lock, and booking confirmation flows.
*   **Security Suite (`tests/security/`)**: Validates input safety, JWT authentication, and rate limiting.
*   **Performance (`tests/performance/`)**: Contains Locust load testing scripts. After profound bottleneck analysis (gRPC singletons, DB connection pool optimization, dropping heavy logging), the local distributed test sustained **1,000 concurrent users** and **600+ Requests Per Second (RPS)** on a single machine with a <5% failure rate (bounded strictly by hardware CPU saturation, not application errors).

---

## 🤡 Phase 1 Retrospective & Hall of Shame
Key errors solved and lessons learned during the integration of the Authentication Service and Performance Tuning:
1.  **UUID Generation Overhead**: Running `uuid.uuid4()` dynamically inside a tight load-test loop completely bottlenecked the test client. Fix: Use integers or fast format strings for dummy IDs when simulating heavy load.
2.  **gRPC Port Exhaustion**: The Gateway initially created a new `grpc.aio.insecure_channel` for every single incoming HTTP request. This led to massive socket/port exhaustion. Fix: Implemented Singleton pattern for gRPC channels, reusing one multiplexed TCP connection.
3.  **Process Collision in Load Testing**: Running Locust with multiple parallel workers caused all virtual users to generate the exact same email address at the exact same millisecond, triggering mass `400 Bad Request` duplicates. Fix: Injected a random unique string suffix into the base user creation routine.
4.  **Bcrypt CPU Wall**: Asymmetric cryptography and native `bcrypt` are incredibly CPU intensive. Under a barrage of 1,000 concurrent users logging in, the Python worker threads saturated 100% of CPU, blocking the asyncio event loop. The 600 RPS limit is the absolute ceiling for a single physical node running these algorithms synchronously. Future scale must be horizontal.
5.  **Private Key Security**: Ensure private keys (`jwt_private.pem`) are kept local/environmental and NEVER committed to GitHub to prevent system-wide compromises.
6.  **Bcrypt Over Passlib**: Nuked deprecated `passlib` due to dependency compatibility issues in modern Python and switched to native `bcrypt` for secure password hashing.