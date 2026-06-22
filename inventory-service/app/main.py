import asyncio
import grpc
from redis.asyncio import Redis

from app.core.config import settings
from app.core.logging import logger

from aerolock_common.generated import inventory_pb2_grpc

from app.services.inventory_service import InventoryService

async def serve():
    redis_client = Redis.from_url(settings.REDIS_URL)
    server = grpc.aio.server()
    
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(
        InventoryService(redis_client), server
    )
    
    port = settings.INVENTORY_PORT
    server.add_insecure_port(f"[::]:{port}")
    
    logger.info(f"Inventory gRPC Service is booting up on port {port}...")
    
    await server.start()
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down Inventory Service...")
        await server.stop(0)
        await redis_client.aclose()

if __name__ == "__main__":
    asyncio.run(serve())