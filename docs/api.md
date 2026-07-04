# API

## Public API (Gateway Service)

### Health

| Method | Path    | Description          |
| ------ | ------- | --------------------- |
| GET    | /health | Service health check |

### Authentication (New Phase 1)

| Method | Path                    | Description                                                    |
| ------ | ----------------------- | -------------------------------------------------------------- |
| POST   | /api/v1/auth/register   | Register a new user with username and password                 |
| POST   | /api/v1/auth/login      | Login and receive an asymmetric RS256 JWT token                |

### Search

| Method | Path            | Description                                 |
| ------ | --------------- | ------------------------------------------- |
| GET    | /api/v1/search/ | Search flights by origin, destination, date |

### Booking

| Method | Path                    | Description                                                                          |
| ------ | ----------------------- | ------------------------------------------------------------------------------------ |
| POST   | /api/v1/booking/lock    | Acquire a temporary lock on a seat (starts 10-min hold)                              |
| POST   | /api/v1/booking/confirm | Confirm booking. **[SECURED]** Requires valid `Authorization: Bearer <JWT_TOKEN>` header. |

### Real-Time (WebSocket)

| Method    | Path                           | Description                                             |
| --------- | ------------------------------ | ------------------------------------------------------- |
| WebSocket | /api/v1/ws/flights/{flight_id} | Subscribe to real-time seat status changes for a flight |

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

---

## Internal gRPC APIs

### User Service (New Phase 1)
Responsible for user registration, authentication, password salting/hashing, and database user ledger. Deployed on port `50053`.

| Method           | Description                                                 |
| ---------------- | ----------------------------------------------------------- |
| RegisterUser     | Register a new user, hashes password using native `bcrypt`. |
| AuthenticateUser | Validate password, returns user details to gateway.         |

### Search Service
Responsible for querying flight availability and serving cached results. Deployed on port `50051`.

| Method        | Description                                                     |
| ------------- | --------------------------------------------------------------- |
| SearchFlights | Return matching flights, served from Redis cache when available |

### Inventory Service
Responsible for seat locking and booking commitment. Deployed on port `50052`.

| Method         | Description                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------------- |
| AcquireLock    | Atomically claim a seat via Redis `SET NX`, returns a lock token                                     |
| ConfirmBooking | Validate lock token (Lua script), re-check Postgres if expired, commit booking with idempotency key |
| ReleaseLock    | Explicitly release a held lock before TTL expiry                                                     |