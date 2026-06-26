import grpc
from fastapi import HTTPException
from aerolock_common.generated import search_pb2, search_pb2_grpc
from app.core.logging import logger

class SearchClient:
    def __init__(self):
        # Search Service runs on 50051
        self.channel = grpc.aio.insecure_channel('localhost:50051')
        self.stub = search_pb2_grpc.SearchServiceStub(self.channel)

    async def search_flights(self, origin: str, destination: str, date: str) -> list[dict]:
        try:
            request = search_pb2.SearchRequest(
                origin=origin,
                destination=destination,
                date=date
            )
            
            response = await self.stub.SearchFlights(request)
            
            # Translate Protobuf to clean Python dicts for the Frontend
            flights = []
            for f in response.flights:
                flights.append({
                    "id": f.id,
                    "origin": f.origin,
                    "destination": f.destination,
                    "departure_time": f.departure_time,
                    "arrival_time": f.arrival_time,
                    "price": f.price,
                    "available_seats": f.available_seats
                })
            return flights
            
        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC Search Connection Error: {e.details()}")
            raise HTTPException(status_code=503, detail="Search Service is currently unavailable")