from fastapi import APIRouter, Depends, Query, Request
from app.clients.search_client import SearchClient
from app.middleware.rate_limit import limiter
from app.schemas.search import FlightResponse
router = APIRouter()

# What the frontend actually receives


async def get_search_client():
    return SearchClient()

@router.get("/", response_model=list[FlightResponse], summary="Search for available flights")
@limiter.limit("20/minute")  # Generous rate limit for searching
async def search_flights(
    request: Request, # Required for SlowAPI
    origin: str = Query(..., min_length=3, max_length=3, description="3-letter airport code (e.g., CAI)"),
    destination: str = Query(..., min_length=3, max_length=3, description="3-letter airport code (e.g., DXB)"),
    date: str = Query(..., description="YYYY-MM-DD format"),
    client: SearchClient = Depends(get_search_client)
):
    # Force uppercase so user stupidity doesn't break the database query
    flights = await client.search_flights(origin.upper(), destination.upper(), date)
    return flights