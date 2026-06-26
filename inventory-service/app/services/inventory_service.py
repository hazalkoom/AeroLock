import grpc

from aerolock_common.generated import inventory_pb2, inventory_pb2_grpc, common_pb2

from app.db.session import Async_session_local
from app.db.repository import InventoryRepository
from app.lock.redis_lock import RedisLockManager
from redis.asyncio import Redis

class InventoryService(inventory_pb2_grpc.InventoryServiceServicer):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def AcquireLock(self, request: inventory_pb2.AcquireLockRequest, context: grpc.aio.ServicerContext) -> inventory_pb2.AcquireLockResponse:
        lock_manager = RedisLockManager(self.redis)
        success, token = await lock_manager.acquire_lock(request.seat_id)

        return inventory_pb2.AcquireLockResponse(
            success=success,
            token=token if token else "",
            message="Lock acquired successfully" if success else "Seat is already locked by someone else."
        )

    async def ConfirmBooking(self, request: inventory_pb2.ConfirmBookingRequest, context: grpc.aio.ServicerContext) -> inventory_pb2.ConfirmBookingResponse:
        lock_manager = RedisLockManager(self.redis)
        lock_key = f"seat:{request.seat_id}:lock"

        stored_token = await self.redis.get(lock_key)
        if not stored_token or stored_token.decode('utf-8') != request.token:
            return inventory_pb2.ConfirmBookingResponse(
                success=False,
                booking_id="",
                message="Lock expired or invalid token. You lost your chance."
            )

        async with Async_session_local() as session:
            repo = InventoryRepository(session)
            success, booking_id = await repo.create_booking(
                seat_id=request.seat_id,
                user_id=request.user_id,
                idempotency_key=request.idempotency_key
            )

            if success:
                await lock_manager.release_lock(request.seat_id, request.token)
                return inventory_pb2.ConfirmBookingResponse(
                    success=True,
                    booking_id=str(booking_id),
                    message="Booking officially confirmed in database."
                )
            else:
                return inventory_pb2.ConfirmBookingResponse(
                    success=False,
                    booking_id="",
                    message="Transaction rejected by the bouncer (Duplicate Idempotency Key)."
                )

    async def ReleaseLock(self, request: inventory_pb2.ReleaseLockRequest, context: grpc.aio.ServicerContext) -> common_pb2.ErrorResponse:
        lock_manager = RedisLockManager(self.redis)
        released = await lock_manager.release_lock(request.seat_id, request.token)

        if released:
            return common_pb2.ErrorResponse(code=0, message="Lock released successfully.")
        return common_pb2.ErrorResponse(code=1, message="Failed to release lock. Token mismatch or lock already expired.")