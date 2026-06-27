# API

## Public API (Gateway Service)

### Health

| Method | Path    | Description          |
| ------ | ------- | --------------------- |
| GET    | /health | Service health check |

### Search

| Method | Path     | Description                                  |
| ------ | -------- | --------------------------------------------- |
| GET    | /api/v1/search/  | Search flights by origin, destination, date  |

### Booking

| Method | Path                        | Description                                              |
| ------ | --------------------------- | --------------------------------------------------------- |
| POST   | /api/v1/booking/lock        | Acquire a temporary lock on a seat (starts 10-min hold)  |
| POST   | /api/v1/booking/confirm     | Confirm a booking after payment (requires idempotency key) |

### Real-Time (WebSocket)

| Method    | Path                                  | Description                                              |
| --------- | ------------------------------------- | --------------------------------------------------------- |
| WebSocket | /api/v1/ws/flights/{flight_id}        | Subscribe to real-time seat status changes for a flight  |

Connect with: `ws://localhost:8000/api/v1/ws/flights/{flight_id}`

The server pushes a JSON message whenever a seat on this flight is locked or confirmed:
```json
{
  "flight_id": "3fa85f64-...",
  "seat_id":   "abc123...",
  "status":    "locked",
  "timestamp": "2026-06-27T11:40:00Z"
}
```
Status values: `"locked"` (10-min hold acquired) or `"confirmed"` (permanently booked).

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