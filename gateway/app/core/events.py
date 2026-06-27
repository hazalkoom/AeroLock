import json
import os
from datetime import datetime, timezone
import redis.asyncio as aioredis

# Global Redis connection — initialized once at gateway startup
_redis: aioredis.Redis | None = None


async def init_redis():
    """Initialize the shared async Redis connection at gateway startup."""
    global _redis
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    _redis = aioredis.from_url(redis_url, decode_responses=True)


async def close_redis():
    """Close the Redis connection at gateway shutdown."""
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def get_redis() -> aioredis.Redis:
    """Return the shared Redis connection. Raises if not initialized."""
    if _redis is None:
        raise RuntimeError("Redis connection not initialized. Call init_redis() first.")
    return _redis


async def publish_seat_event(flight_id: str, seat_id: str, status: str):
    """
    Publish a seat status change event to all WebSocket clients
    watching this flight via Redis Pub/Sub.

    Args:
        flight_id: The UUID of the flight.
        seat_id:   The UUID of the seat that changed status.
        status:    Either "locked" or "confirmed".
    """
    try:
        r = get_redis()
        channel = f"seat_events:{flight_id}"
        payload = json.dumps({
            "flight_id": flight_id,
            "seat_id": seat_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        await r.publish(channel, payload)
    except Exception:
        # Never let a Redis publish failure break the booking flow
        pass
