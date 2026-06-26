import asyncio
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Connection to the shared Postgres DB
DATABASE_URL = "postgresql+asyncpg://aerolock_user:password123@localhost:5432/aerolock"

CITIES = ["Cairo", "Dubai", "London", "New York", "Paris", "Tokyo", "Berlin", "Riyadh"]

async def seed_db():
    print("Connecting to database...")
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        print("Wiping old data (TRUNCATE CASCADE)...")
        # Nuke the tables so we don't get duplicate errors
        await conn.execute(text("TRUNCATE TABLE seats, bookings, flights CASCADE;"))
        
        print("Generating 100 flights...")
        flights = []
        
        # 1. GUARANTEED TEST FLIGHT (So your test client actually finds something)
        flights.append({
            "id": str(uuid.uuid4()),
            "origin": "Cairo",
            "destination": "Dubai",
            "departure_time": "2026-12-01 10:00:00",
            "arrival_time": "2026-12-01 14:00:00",
            "price": 350.00
        })
        
        # 2. Generate 99 random flights
        for _ in range(99):
            origin = random.choice(CITIES)
            dest = random.choice([c for c in CITIES if c != origin])
            
            # Random date around late Nov / early Dec 2026
            day_offset = random.randint(-5, 10)
            hour_offset = random.randint(0, 23)
            dep_time = datetime(2026, 12, 1) + timedelta(days=day_offset, hours=hour_offset)
            arr_time = dep_time + timedelta(hours=random.randint(2, 14)) # 2 to 14 hour flights
            
            flights.append({
                "id": str(uuid.uuid4()),
                "origin": origin,
                "destination": dest,
                "departure_time": dep_time.strftime("%Y-%m-%d %H:%M:%S"),
                "arrival_time": arr_time.strftime("%Y-%m-%d %H:%M:%S"),
                "price": round(random.uniform(150.0, 1200.0), 2)
            })
        
        # Insert all flights
        flight_query = text("""
            INSERT INTO flights (id, origin, destination, departure_time, arrival_time, price)
            VALUES (:id, :origin, :destination, CAST(:departure_time AS TIMESTAMP), CAST(:arrival_time AS TIMESTAMP), :price)
        """)
        
        await conn.execute(flight_query, flights)
        
        print("Generating 15,000 seats (150 per flight)...")
        seats = []
        for f in flights:
            for row in range(1, 26): # 25 rows
                for letter in ['A', 'B', 'C', 'D', 'E', 'F']: # 6 seats per row = 150 seats per flight
                    seats.append({
                        "id": str(uuid.uuid4()),
                        "flight_id": f["id"],
                        "seat_number": f"{row}{letter}",
                        "status": "available"
                    })
        
        # Batch insert seats so we don't blow up RAM
        seat_query = text("""
            INSERT INTO seats (id, flight_id, seat_number, status)
            VALUES (:id, :flight_id, :seat_number, :status)
        """)
        
        chunk_size = 5000
        for i in range(0, len(seats), chunk_size):
            print(f"Inserting seats {i} to {i+chunk_size}...")
            await conn.execute(seat_query, seats[i:i+chunk_size])

    print("✅ BOOM! Database successfully seeded with 100 flights and 15,000 seats!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_db())