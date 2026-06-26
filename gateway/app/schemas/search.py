from pydantic import BaseModel


class FlightResponse(BaseModel):
    id: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    price: float
    available_seats: int