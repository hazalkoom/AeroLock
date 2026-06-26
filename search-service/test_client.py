import asyncio
import grpc
from aerolock_common.generated import search_pb2, search_pb2_grpc

async def test_search():
    print("Connecting to Search Service at localhost:50051...")
    
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = search_pb2_grpc.SearchServiceStub(channel)
        
        request = search_pb2.SearchRequest(
            origin="CAI",
            destination="DXB",
            date="2026-12-01"
        )
        
        print("Sending search request for Cairo to Dubai on 2026-12-01...\n")
        response = await stub.SearchFlights(request)
        
        if not response.flights:
            print("No flights found. Database might be empty or query failed.")
            return

        print(f"Success! Found {len(response.flights)} flights:\n")
        for f in response.flights:
            print(f"Flight ID: {f.id}")
            print(f"Route: {f.origin} -> {f.destination}")
            print(f"Available Seats: {f.available_seats}")
            print(f"Price: ${f.price}")
            print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_search())