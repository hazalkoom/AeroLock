import asyncio
import grpc
from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import logger

from aerolock_common.generated import inventory_pb2_grpc

from app.services.inventory_service import InventoryService

async def serve():
    # 1. Initialize the Redis client using the validated URL from core/config.py
    redis_client = Redis.from_url(settings.REDIS_URL)

    # 2. Create the asynchronous gRPC server
    server = grpc.aio.server()

    # 3. Attach our InventoryService logic to the gRPC server
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(
        InventoryService(redis_client), server
    )

    # 4. Bind the server to the port defined in our settings
    port = settings.INVENTORY_PORT
    server.add_insecure_port(f"[::]:{port}")

    logger.info(f"Inventory gRPC Service is booting up on port {port}...")

    # 5. Start the server and keep it alive
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down Inventory Service...")
        await server.stop(0)
        await redis_client.aclose()

if __name__ == "__main__":
    # Run the async loop
    asyncio.run(serve())