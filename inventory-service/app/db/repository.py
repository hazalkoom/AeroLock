from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .models import Seat, Booking
import logging

logger = logging.getLogger(__name__)

class InventoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_seat(self, seat_id: str):
        result = await self.session.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalar_one_or_none()

    async def create_booking(self, seat_id: str, user_id: str, idempotency_key: str):
        try:
            # 1. Fetch the seat to update its status
            seat = await self.get_seat(seat_id)
            if not seat or seat.status != 'available':
                return False, "Seat is not available"

            # 2. Mark the seat as booked
            seat.status = 'booked'

            # 3. Create the booking record
            new_booking = Booking(
                seat_id=seat_id, 
                user_id=user_id, 
                idempotency_key=idempotency_key
            )
            self.session.add(new_booking)
            
            # 4. Commit both the seat update and the new booking atomically
            await self.session.commit()
            return True, str(new_booking.id)
            
        except IntegrityError:
            # THE BOUNCER WORKED: Duplicate idempotency_key detected
            await self.session.rollback()
            return False, "Duplicate booking request (Idempotency Key collision)"
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Database error during booking: {e}")
            return False, "Internal database error"