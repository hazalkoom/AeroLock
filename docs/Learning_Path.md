# Learning Path & Resources

This document maps each phase of building AeroLock to the concepts you'll
need, with resources for each. Use it as a checklist — you don't need to
"finish learning" any topic before starting; learn just enough to take the
next step, then come back when you hit a wall.

---

## Phase 1 — Contracts: Protocol Buffers & gRPC

**What you're doing:** writing `.proto` files that define how the Gateway
talks to the Search and Inventory services.

**Concepts:** message types, service definitions, generating Python stubs.

**Resources:**
- gRPC Python quickstart — https://grpc.io/docs/languages/python/quickstart/
- Protocol Buffers language guide (proto3) — https://protobuf.dev/programming-guides/proto3/
- gRPC Python basics tutorial — https://grpc.io/docs/languages/python/basics/

---

## Phase 2 — Core Logic: FastAPI, Redis Locking, PostgreSQL

**What you're doing:** building the Inventory Service — the heart of the
project.

### FastAPI
- Official tutorial — https://fastapi.tiangolo.com/tutorial/
- Async/await in FastAPI — https://fastapi.tiangolo.com/async/

### Redis distributed locks
- Redis distributed locks docs — https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/
- "How to do distributed locking" (Kleppmann) — https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
- redis-py client docs — https://redis-py.readthedocs.io/

### Lua scripting in Redis
- EVAL/Lua scripting docs — https://redis.io/docs/latest/develop/programmability/eval-intro/
- Why Lua scripts are atomic — same redis.io page above, "Atomicity of scripts" section

### PostgreSQL + Python
- asyncpg (async Postgres driver) — https://magicstack.github.io/asyncpg/current/
- SQLAlchemy 2.0 async ORM — https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- `ON CONFLICT` (upsert) docs — https://www.postgresql.org/docs/current/sql-insert.html#SQL-ON-CONFLICT

---

## Phase 3 — Search Service: Caching Patterns

**What you're doing:** building the Search Service — Redis cache in front
of PostgreSQL.

**Concepts:** cache-aside pattern, TTL-based invalidation.

**Resources:**
- Caching strategies overview — https://redis.io/docs/latest/develop/use/caching/
- Redis EXPIRE / TTL docs — https://redis.io/docs/latest/commands/expire/

---

## Phase 4 — Gateway: Routing, Rate Limiting, Error Translation

**What you're doing:** the public-facing REST layer.

**Concepts:** gRPC clients in Python, HTTP status code mapping, rate limiting
middleware.

**Resources:**
- FastAPI middleware — https://fastapi.tiangolo.com/tutorial/middleware/
- slowapi (rate limiting for FastAPI) — https://github.com/laurentS/slowapi
- gRPC status codes — https://grpc.io/docs/guides/status-codes/

---

## Phase 5 — Integration: Docker & Docker Compose

**What you're doing:** making all services run together locally and on
the VPS.

**Resources:**
- Docker Compose overview — https://docs.docker.com/compose/
- Multi-stage Dockerfile builds (smaller images) — https://docs.docker.com/build/building/multi-stage/
- Docker Compose healthchecks — https://docs.docker.com/reference/compose-file/services/#healthcheck

---

## Phase 6 — Testing

### pytest basics
- pytest docs — https://docs.pytest.org/en/stable/
- pytest fixtures — https://docs.pytest.org/en/stable/how-to/fixtures.html
- pytest-asyncio (for async test functions) — https://pytest-asyncio.readthedocs.io/

### Testing concurrency (the core demo)
- Python `asyncio.gather` for firing concurrent requests — https://docs.python.org/3/library/asyncio-task.html#asyncio.gather
- httpx AsyncClient (for concurrent HTTP calls in tests) — https://www.python-httpx.org/async/

### Performance testing
- Locust docs — https://docs.locust.io/en/stable/
- k6 docs — https://k6.io/docs/
- k6 vs Locust comparison (helps you pick) — https://k6.io/docs/testing-guides/load-testing-vs-stress-testing/

### Security testing
- OWASP ZAP baseline scan — https://www.zaproxy.org/docs/docker/baseline-scan/
- OWASP API Security Top 10 (for context on what to check) — https://owasp.org/www-project-api-security/

---

## Phase 7 — Deployment

**Resources:**
- Nginx reverse proxy guide — https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
- Certbot (Let's Encrypt) — https://certbot.eff.org/instructions
- Hetzner Cloud getting started — https://docs.hetzner.com/cloud/

---

## Phase 8 (Stretch) — Kubernetes (ideal architecture, not MVP)

Only explore this once the MVP is deployed and working. The manifests in
`k8s/` are for the planning document's "ideal architecture" section — you
don't need to actually run a cluster for the MVP.

- Kubernetes basics — https://kubernetes.io/docs/tutorials/kubernetes-basics/
- Kustomize (used for `k8s/overlays/`) — https://kubectl.docs.kubernetes.io/guides/introduction/kustomize/

---

## General Reference

- Real Python (high-quality tutorials across all of the above) — https://realpython.com/
- "Designing Data-Intensive Applications" by Martin Kleppmann — the
  conceptual foundation for everything in Phase 2 (library/used copy
  recommended, not free, but the single best resource for this project's
  core ideas)

---

## How to Use This With AI Agents

When you hit a wall on a specific phase, paste the relevant section of this
file plus `AGENT_CONTEXT.md` into your AI tool of choice along with your
specific question. The combination gives the model both the *project*
context and the *concept* you're trying to learn, so it can explain in
terms of your actual code rather than generic examples.