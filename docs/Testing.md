# Testing

AeroLock's testing strategy mirrors the project's two consistency paths:
**correctness** matters most for the booking (CP) path, **performance**
matters most for the search (AP) path. Security testing covers the Gateway's
public surface.

## Test Layers

| Layer       | Location                              | What it proves                                  |
| ------------ | ---------------------------------------- | ---------------------------------------------------- |
| Unit         | `<service>/tests/unit/`                  | Individual functions (lock acquisition, cache, repository queries) work in isolation |
| E2E          | `tests/e2e/`                              | Full request flow across all 3 services via docker-compose |
| Performance  | `tests/performance/`                     | System meets the RPS/latency targets from Requirements.md |
| Security     | `tests/security/`                        | Rate limiting, input validation hold under abuse |

---

## 1. Unit Tests

Each service has its own `tests/unit/` directory and runs independently —
no Docker required, mocked Redis/Postgres.

```bash
cd inventory-service
pytest tests/unit -v
```

Key unit tests:

- `test_redis_lock.py` — `SET NX PX` acquisition, Lua script token validation
- `test_idempotency.py` — duplicate `idempotency_key` is a no-op, not an error
- `test_repository.py` — booking/seat queries return expected rows

## 2. End-to-End Tests

E2E tests run against the full docker-compose stack.

```bash
docker-compose up -d
pytest tests/e2e -v
```

**The most important test in the entire suite:**

```bash
pytest tests/e2e/test_concurrent_booking.py -v
```

This fires two simultaneous `AcquireLock` requests for the same seat and
asserts:
- exactly one returns `200 OK` with a lock token
- the other returns `423 Locked`
- the seat is never double-booked in PostgreSQL

This is the test to show in your demo video.

Other E2E tests:

- `test_search_flow.py` — search returns results, second identical search
  hits the Redis cache (check via response header or timing)
- `test_booking_flow.py` — full lock -> pay -> confirm happy path
- `test_idempotent_retry.py` — confirming the same booking twice with the
  same idempotency key produces one booking, not two

## 3. Performance Tests

Validates the RPS/latency targets from `Requirements.md`:
Search p95 < 80 ms, Booking lock p95 < 50 ms, 18.5 RPS search / 0.37 RPS booking.

### Locust (Python, good for mixed scenarios)

```bash
cd tests/performance
locust -f locustfile.py --host http://localhost:8000
```
Open `http://localhost:8089`, set users/spawn rate, run, check p95 in the UI.

### k6 (better for raw throughput numbers)

```bash
k6 run tests/performance/k6_search.js
k6 run tests/performance/k6_booking.js
```

Record results in `tests/performance/README.md` — include a screenshot or
output table in your final submission as evidence the targets are met.

## 4. Security Tests

Given D-004 (no auth in v1), security tests focus on what *is* implemented:

```bash
pytest tests/security -v
```

- `test_rate_limiting.py` — 101st request within a minute returns `429`
- `test_input_validation.py` — malformed search params / booking payloads
  return `422`, not `500`
- `test_auth_headers.py` — confirms missing/invalid API key behavior matches
  documented design (even if "no auth" — verify the key is at least logged)

### Optional: OWASP ZAP baseline scan

```bash
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://<vps-ip>:80 -c tests/security/zap-baseline.conf
```

Run this once against the deployed VPS before final submission — include
the summary report as evidence in your README.

---

## Running Everything

```bash
./scripts/run_e2e_tests.sh
./scripts/run_performance_tests.sh
./scripts/run_security_tests.sh
```

## CI

`.github/workflows/ci.yml` runs unit tests on every push.
`.github/workflows/e2e.yml` spins up docker-compose and runs the E2E suite.
`.github/workflows/security.yml` runs the security test subset.

Keep these green — a passing CI badge in the README is good evidence for
reviewers that the project actually runs.