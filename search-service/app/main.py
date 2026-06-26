print("--- SCRIPT IS EXECUTING ---")

import asyncio
import grpc
from app.core.config import settings
from app.core.logging import logger
from aerolock_common.generated import search_pb2_grpc
from app.server import SearchServiceServicer

async def serve():
    print("--- INSIDE SERVE FUNCTION ---")
    server = grpc.aio.server()
    search_pb2_grpc.add_SearchServiceServicer_to_server(SearchServiceServicer(), server)
    
    listen_addr = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    
    print(f"--- SERVER BINDING TO PORT {settings.GRPC_PORT} ---")
    logger.info(f"Search gRPC Service is booting up on port {settings.GRPC_PORT}...")
    
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    print("--- ENTRY POINT TRIGGERED ---")
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Server shutting down gracefully...")
    except Exception as e:
        print(f"--- FATAL CRASH: {e} ---")