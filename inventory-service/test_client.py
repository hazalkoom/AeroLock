import asyncio
import grpc
import uuid

from aerolock_common.generated import inventory_pb2, inventory_pb2_grpc

TARGET_SEAT_ID = "e3e3df56-5c88-41f6-bb4d-9e44810aa585"
USER_ID = "hazalkoom_user_99"

async def test_booking_flow():
    print("Connecting to Inventory Service at localhost:50052...")
    
    # We use insecure_channel because we aren't using SSL certificates locally
    async with grpc.aio.insecure_channel('localhost:50052') as channel:
        stub = inventory_pb2_grpc.InventoryServiceStub(channel)

        print(f"\n--- 1. Attempting to Acquire Lock for Seat {TARGET_SEAT_ID} ---")
        lock_request = inventory_pb2.AcquireLockRequest(seat_id=TARGET_SEAT_ID)
        lock_response = await stub.AcquireLock(lock_request)

        print(f"Success: {lock_response.success}")
        print(f"Message: {lock_response.message}")
        print(f"Token: {lock_response.token}")

        if not lock_response.success:
            print("Failed to lock. Seat might be taken. Exiting.")
            return

        print("\n--- 2. Confirming Booking in PostgreSQL ---")
        # Generate a random idempotency key. If you sent the exact same key twice, 
        # the database would reject the second one to prevent double-charging the user.
        idem_key = str(uuid.uuid4())
        
        book_request = inventory_pb2.ConfirmBookingRequest(
            seat_id=TARGET_SEAT_ID,
            user_id=USER_ID,
            idempotency_key=idem_key,
            token=lock_response.token
        )
        
        book_response = await stub.ConfirmBooking(book_request)
        
        print(f"Success: {book_response.success}")
        print(f"Message: {book_response.message}")
        print(f"Booking ID: {book_response.booking_id}")

if __name__ == "__main__":
    asyncio.run(test_booking_flow())