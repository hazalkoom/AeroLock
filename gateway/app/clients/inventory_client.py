import grpc
from fastapi import HTTPException
import os
from aerolock_common.generated import inventory_pb2, inventory_pb2_grpc

class InventoryClient:
    def __init__(self):
        # Establish an asynchronous channel to the Inventory Service
        inventory_service_url = os.getenv("INVENTORY_SERVICE_URL", "inventory-service:50052")
        self.channel = grpc.aio.insecure_channel(inventory_service_url)
        self.stub = inventory_pb2_grpc.InventoryServiceStub(self.channel)

    async def acquire_lock(self, seat_id: str) -> dict:
        try:
            request = inventory_pb2.AcquireLockRequest(seat_id=seat_id)
            response = await self.stub.AcquireLock(request)
            
            if not response.success:
                # 409 Conflict: The seat is already locked by someone else
                raise HTTPException(status_code=409, detail=response.message)
                
            return {
                "success": response.success, 
                "token": response.token, 
                "message": response.message
            }
        except grpc.aio.AioRpcError as e:
            # 500 Internal Server Error: The Inventory Service is dead or unreachable
            raise HTTPException(status_code=500, detail=f"gRPC Error: {e.details()}")

    async def confirm_booking(self, seat_id: str, user_id: str, idempotency_key: str, token: str) -> dict:
        try:
            request = inventory_pb2.ConfirmBookingRequest(
                seat_id=seat_id,
                user_id=user_id,
                idempotency_key=idempotency_key,
                token=token
            )
            response = await self.stub.ConfirmBooking(request)
            
            if not response.success:
                # 400 Bad Request: Token expired or duplicate idempotency key
                raise HTTPException(status_code=400, detail=response.message)
                
            return {
                "success": response.success, 
                "booking_id": response.booking_id, 
                "message": response.message
            }
        except grpc.aio.AioRpcError as e:
            raise HTTPException(status_code=500, detail=f"gRPC Error: {e.details()}")