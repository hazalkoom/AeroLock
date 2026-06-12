# AeroLock

AeroLock is a real-time, distributed backend API engine that prevents
double-booking of flight seats using a Redis distributed lock and a
PostgreSQL ACID ledger.

## What it does

- Serves flight search results from a Redis cache for low-latency reads.
- Acquires a distributed lock on a seat the instant a user clicks "Book",
  preventing two users from holding the same seat.
- Confirms bookings with idempotency keys, so retried payment webhooks
  never create duplicate bookings.

## How it works

A client searches for flights via the Gateway, which queries the Search
Service (Redis-cached, PostgreSQL-backed). To book, the client requests a
seat lock from the Inventory Service (`SET NX` in Redis, 12-minute TTL).
After simulated payment, the client confirms the booking, which validates
the lock token and commits to PostgreSQL.

## How to install

See [Deployment](docs/Deployment.md).

## More about it

- [Requirements](docs/Requirements.md)
- [Architecture](docs/Architecture.md)
- [Design Decisions](docs/Design_Decisions.md)
- [API Reference](docs/api.md)
- [Deployment](docs/Deployment.md)
- [Free Deployment (No Credit Card)](docs/Deployment_Free.md)
- [Testing](docs/Testing.md)
- [Learning Path & Resources](docs/Learning_Path.md)