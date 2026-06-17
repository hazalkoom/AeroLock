import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .session import Base

class Flight(Base):
    __tablename__ = "flights"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    origin = Column(String(10), nullable=False)
    destination = Column(String(10), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    total_seats = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

class Seat(Base):
    __tablename__ = "seats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_id = Column(UUID(as_uuid=True), ForeignKey("flights.id", ondelete="CASCADE"), nullable=False)
    seat_number = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default="available")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False)
    user_id = Column(String(255), nullable=False)
    idempotency_key = Column(String(255), unique=True, nullable=False)
    status = Column(String(20), nullable=False, default="confirmed")