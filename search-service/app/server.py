import grpc
from aerolock_common.generated import search_pb2, search_pb2_grpc
from app.cache import CacheManager
from app.db.session import AsyncSessionLocal
from app.db.repository import SearchRepository
from app.core.logging import logger

class SearchServiceServicer(search_pb2_grpc.SearchServiceServicer):
    def __init__(self):
        self.cache = CacheManager()

    async def SearchFlights(self, request: search_pb2.SearchRequest, context: grpc.aio.ServicerContext) -> search_pb2.SearchResponse:
        logger.info(f"Received search request: {request.origin} -> {request.destination} on {request.date}")

        # 1. Check Redis First
        cached_flights = await self.cache.get_cached_search(
            request.origin, request.destination, request.date
        )

        if cached_flights is not None:
            return self._build_response(cached_flights)

        # 2. CACHE MISS: Query Postgres
        async with AsyncSessionLocal() as session:
            repo = SearchRepository(session)
            db_flights = await repo.search_flights(
                request.origin, request.destination, request.date
            )

        # 3. Save to Redis
        await self.cache.set_cached_search(
            request.origin, request.destination, request.date, db_flights
        )

        return self._build_response(db_flights)

    def _build_response(self, flights_data: list[dict]) -> search_pb2.SearchResponse:
        response = search_pb2.SearchResponse()
        for f in flights_data:
            flight_pb = response.flights.add()
            flight_pb.id = f["flight_id"] 
            flight_pb.origin = f["origin"]
            flight_pb.destination = f["destination"]
            flight_pb.departure_time = f["departure_time"]
            flight_pb.arrival_time = f["arrival_time"]
            flight_pb.price = f["price"]
            flight_pb.available_seats = f["available_seats"]
        return response