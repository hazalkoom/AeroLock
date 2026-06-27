import asyncio
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

# Connection to the shared Postgres DB
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://aerolock_user:password123@localhost:5432/aerolock")

# Using 3-letter codes to strictly respect your VARCHAR(10) schema limit
CITIES = ["CAI", "DXB", "LHR", "JFK", "PAR", "TYO", "BER", "RUH"]

async def seed_db():
    print("Connecting to database...")
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        print("Wiping old data (TRUNCATE CASCADE)...")
        # Nuke the tables so we don't get duplicate errors
        await conn.execute(text("TRUNCATE TABLE seats, bookings, flights CASCADE;"))
        
        print("Generating 100 flights...")
        flights = []
        
        # 1. GUARANTEED TEST FLIGHT (Using native datetime objects for asyncpg)
        flights.append({
            "id": str(uuid.uuid4()),
            "origin": "CAI",
            "destination": "DXB",
            "departure_time": datetime(2026, 12, 1, 10, 0, 0),
            "arrival_time": datetime(2026, 12, 1, 14, 0, 0),
            "total_seats": 150, # Explicitly adding this to match your schema
            "price": 350.00
        })
        
        # 2. Generate 99 random flights
        for _ in range(99):
            origin = random.choice(CITIES)
            dest = random.choice([c for c in CITIES if c != origin])
            
            day_offset = random.randint(-5, 10)
            hour_offset = random.randint(0, 23)
            dep_time = datetime(2026, 12, 1) + timedelta(days=day_offset, hours=hour_offset)
            arr_time = dep_time + timedelta(hours=random.randint(2, 14))
            
            flights.append({
                "id": str(uuid.uuid4()),
                "origin": origin,
                "destination": dest,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "total_seats": 150,
                "price": round(random.uniform(150.0, 1200.0), 2)
            })
        
        # Insert all flights (NO flight_number, YES total_seats)
        flight_query = text("""
            INSERT INTO flights (id, origin, destination, departure_time, arrival_time, total_seats, price)
            VALUES (:id, :origin, :destination, :departure_time, :arrival_time, :total_seats, :price)
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
                        "status": "available" # lowercase to match your schema
                    })
        
        # Batch insert seats
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