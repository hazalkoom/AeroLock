import asyncio
import os
import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/flights/{flight_id}")
async def seat_availability_ws(websocket: WebSocket, flight_id: str):
    """
    WebSocket endpoint: stream real-time seat status changes for a flight.

    Connect to: ws://localhost:8000/api/v1/ws/flights/{flight_id}

    The client receives a JSON message whenever a seat on this flight
    is locked or confirmed via the REST booking endpoints:

    {
        "flight_id": "...",
        "seat_id":   "...",
        "status":    "locked" | "confirmed",
        "timestamp": "2026-..."
    }
    """
    await websocket.accept()

    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    pubsub_redis = aioredis.from_url(redis_url, decode_responses=True)
    pubsub = pubsub_redis.pubsub()
    channel = f"seat_events:{flight_id}"

    try:
        await pubsub.subscribe(channel)

        # Send a welcome message so the client knows they're connected
        await websocket.send_json({
            "type": "connected",
            "flight_id": flight_id,
            "message": f"Subscribed to real-time seat events for flight {flight_id}",
        })

        while True:
            # Poll Redis for new messages, with a small sleep to avoid busy-looping
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])

            # Yield control so FastAPI can handle disconnects / other requests
            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        # Client disconnected cleanly — nothing to do
        pass
    except Exception:
        # On any unexpected error, close the socket gracefully
        try:
            await websocket.close()
        except Exception:
            pass
    finally:
        # Always clean up the Redis subscription
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
            await pubsub_redis.aclose()
        except Exception:
            pass
