from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .models import Seat, Booking

class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_seat(self, seat_id: str):
        # Queries the database for a specific seat object
        result = await self.session.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalar_one_or_none()

    async def create_booking(self, seat_id: str, user_id: str, idempotency_key: str):
        new_booking = Booking(
            seat_id=seat_id, 
            user_id=user_id, 
            idempotency_key=idempotency_key
        )
        self.session.add(new_booking)
        
        try:
            # Try to save it to Postgres
            await self.session.commit()
            return True, new_booking.id
        except IntegrityError:
            # THE BOUNCER WORKED: Duplicate idempotency_key detected
            await self.session.rollback()
            return False, None