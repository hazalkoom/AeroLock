# Decisions

## D-001: Backend Framework

**Decision**:
Use FastAPI for all three services (Gateway, Search, Inventory).

**Reason**:
Async-native, ideal for I/O-bound gRPC workers. Strong type validation via
Pydantic. Automatic OpenAPI docs for the Gateway's public API. One framework
across all services keeps shared code (config, logging) reusable.

---

## D-002: Internal Communication

**Decision**:
gRPC + Protobuf between Gateway, Search Service, and Inventory Service.

**Reason**:
Typed contracts via `.proto` files catch integration errors at compile time.
Binary serialization reduces internal latency by roughly 30% versus
REST/JSON, which matters on the booking critical path.

---

## D-003: Distributed Locking

**Decision**:
Single Redis node, `SET key value NX PX <ttl>` for atomic lock acquisition,
with a Lua script for token-validated release/confirm.

**Reason**:
Sub-millisecond acquisition. Redlock (multi-node) adds operational
complexity unjustified at 18.5 peak RPS. AOF persistence means a Redis
restart does not silently drop active locks.

---

## D-004: Authentication

**Decision**:
No authentication in v1. Rate limiting is per API key, but key issuance is
out of scope for the MVP (a static key list is acceptable).

**Reason**:
Reduces complexity; the project's focus is the locking/consistency
mechanism, not identity management.

---

## D-005: Database

**Decision**:
PostgreSQL for flights, seats, and bookings.

**Reason**:
ACID transactions and `ON CONFLICT (idempotency_key) DO NOTHING` are
required for a financial ledger. Strong relational modeling fits the
flight/seat/booking relationships naturally.

---

## D-006: Idempotency

**Decision**:
Every write operation (booking confirmation) requires a client-supplied
idempotency key, enforced as a UNIQUE constraint in PostgreSQL.

**Reason**:
Payment webhooks can fire more than once. Idempotency keys make retries
safe without additional deduplication infrastructure.

---

## D-007: Shared Code Package

**Decision**:
Common code (config loading, structured logging, Redis client factory,
generated gRPC stubs) lives in `shared/aerolock-common/` and is installed
by each service as a local editable package.

**Reason**:
Avoids triplicating boilerplate across Gateway, Search, and Inventory
services. Generated `.proto` stubs are produced once and consumed by all
three, preventing drift between copies.

---

## D-008: Deployment Model (MVP)

**Decision**:
Docker Compose on a single VPS (Hetzner CPX31) for the MVP deployment.
Kubernetes manifests are written and included in the repo as the
**ideal production architecture**, but are not the MVP deploy target.

**Reason**:
At 18.5 peak RPS, a single VPS has massive headroom. Running a k8s cluster
for this load would be operational overhead with no functional benefit,
and would consume time better spent on the locking logic itself.

---

## D-009: Mocked External Dependencies

**Decision**:
No real Amadeus/GDS integration and no real payment processor. Flight
inventory is seeded directly into PostgreSQL; payment confirmation is a
mock webhook endpoint with configurable simulated latency.

**Reason**:
GDS APIs require certification and cost money. Real payment processors
require PCI-DSS compliance. Both are explicitly out of scope, and mocking
them still allows the core locking mechanism to be demonstrated end to end.

---

## D-010: Rate Limiting

**Decision**:
Fixed rate limit of 100 requests/minute per API key, enforced at the
Gateway with an in-memory counter.

**Reason**:
Adaptive/ML-based throttling is out of scope for the MVP. A fixed limit is
sufficient to demonstrate abuse protection without a monitoring pipeline.