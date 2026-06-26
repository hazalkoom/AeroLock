import asyncio
import sys
import os
from datetime import datetime, timedelta, UTC

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import Async_session_local
from app.db.models import Flight, Seat

async def seed_database():
    print("Starting database seed...")
    async with Async_session_local() as session:
        # Create Flight 1 (Cairo to Dubai)
        flight1 = Flight(
            origin="CAI",
            destination="DXB",
            departure_time=datetime.now(UTC) + timedelta(days=5),
            arrival_time=datetime.now(UTC) + timedelta(days=5, hours=3),
            total_seats=10,
            price=250.00
        )
        
        # Create Flight 2 (London to New York)
        flight2 = Flight(
            origin="LHR",
            destination="JFK",
            departure_time=datetime.now(UTC) + timedelta(days=10),
            arrival_time=datetime.now(UTC) + timedelta(days=10, hours=8),
            total_seats=10,
            price=450.00
        )

        session.add(flight1)
        session.add(flight2)
        await session.commit()
        
        # We need the generated IDs to attach the seats
        await session.refresh(flight1)
        await session.refresh(flight2)

        print(f"Created Flight 1: {flight1.id} | CAI -> DXB")
        print(f"Created Flight 2: {flight2.id} | LHR -> JFK")

        # Create 10 seats for each flight
        for i in range(1, 11):
            session.add(Seat(flight_id=flight1.id, seat_number=f"{i}A", status="available"))
            session.add(Seat(flight_id=flight2.id, seat_number=f"{i}B", status="available"))

        await session.commit()
        print("Successfully seeded 2 flights and 20 seats into PostgreSQL!")

if __name__ == "__main__":
    asyncio.run(seed_database())