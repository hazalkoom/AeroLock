# API

## Public API (Gateway Service)

### Health

| Method | Path    | Description          |
| ------ | ------- | --------------------- |
| GET    | /health | Service health check |

### Search

| Method | Path     | Description                                  |
| ------ | -------- | --------------------------------------------- |
| GET    | /search  | Search flights by origin, destination, date  |

### Booking

| Method | Path                | Description                                              |
| ------ | ------------------- | --------------------------------------------------------- |
| POST   | /bookings/lock      | Acquire a temporary lock on a seat (starts 10-min hold)  |
| POST   | /bookings/confirm   | Confirm a booking after payment (requires idempotency key) |
| DELETE | /bookings/lock/{id} | Release a held lock before it expires                    |
| GET    | /bookings/{id}      | Get booking status                                       |

### Status Codes Worth Noting

| Code | Meaning                                                |
| ---- | ------------------------------------------------------- |
| 200  | Success                                                |
| 423  | Seat lock already held by another client (try again)  |
| 409  | Idempotency key conflict (duplicate confirm, no-op)   |
| 429  | Rate limit exceeded (100 req/min per API key)         |

---

## Internal gRPC APIs

### Search Service

Responsible for querying flight availability and serving cached results.

| Method        | Description                                          |
| -------------- | ------------------------------------------------------ |
| SearchFlights | Return matching flights, served from Redis cache when available |

### Inventory Service

Responsible for seat locking and booking commitment.

| Method          | Description                                                        |
| ---------------- | --------------------------------------------------------------------- |
| AcquireLock     | Atomically claim a seat via Redis `SET NX`, returns a lock token  |
| ConfirmBooking  | Validate lock token (Lua script), re-check Postgres if expired, commit booking with idempotency key |
| ReleaseLock     | Explicitly release a held lock before TTL expiry                  |

---

## Processing Flow — Search (AP path)

```text
Client
  |
GET /search
  |
Gateway Service
  |
SearchFlights()
  |
Search Service
  |
Redis cache (hit) --or-- PostgreSQL (miss, then cache)
```

## Processing Flow — Booking (CP path)

```text
Client
  |
POST /bookings/lock
  |
Gateway Service
  |
AcquireLock()
  |
Inventory Service
  |
Redis SET NX (seat lock, 12-min TTL)
  |
  v
[ Client pays via simulated gateway ]
  |
POST /bookings/confirm  (idempotency key)
  |
Gateway Service
  |
ConfirmBooking()
  |
Inventory Service
  |
Lua script: validate token --> release lock
  |
  +-- if lock expired: re-check seat availability in PostgreSQL
  |
PostgreSQL INSERT ... ON CONFLICT (idempotency_key) DO NOTHING
```