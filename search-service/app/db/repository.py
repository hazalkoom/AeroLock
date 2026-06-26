from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from app.core.logging import logger

class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_flights(self, origin: str, destination: str, departure_date_str: str) -> list[dict]:
        # FIX 1: Convert the string "2026-12-01" into a native Python date object
        try:
            target_date = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid date format received: {departure_date_str}")
            return []


        query = text("""
            SELECT 
                f.id as flight_id,
                f.origin,
                f.destination,
                f.departure_time,
                f.arrival_time,
                f.price,
                COUNT(s.id) as available_seats
            FROM flights f
            LEFT JOIN seats s ON f.id = s.flight_id AND s.status = 'available'
            WHERE LOWER(f.origin) = LOWER(:origin)
              AND LOWER(f.destination) = LOWER(:destination)
              AND DATE(f.departure_time) = :departure_date
            GROUP BY f.id
            HAVING COUNT(s.id) > 0;
        """)
        
        try:
            result = await self.session.execute(
                query, 
                {
                    "origin": origin.lower(), 
                    "destination": destination.lower(), 
                    "departure_date": target_date # Passing the native Date object!
                }
            )
            
            flights = []
            for row in result.mappings():
                flights.append({
                    "flight_id": str(row["flight_id"]),
                    "origin": row["origin"],
                    "destination": row["destination"],
                    "departure_time": row["departure_time"].isoformat(),
                    "arrival_time": row["arrival_time"].isoformat(),
                    "price": float(row["price"]),
                    "available_seats": row["available_seats"]
                })
                
            return flights
            
        except Exception as e:
            logger.error(f"Database Search Error: {e}")
            return []