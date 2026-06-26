from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Flight(_message.Message):
    __slots__ = ("id", "origin", "destination", "departure_time", "arrival_time", "price", "available_seats")
    ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    DEPARTURE_TIME_FIELD_NUMBER: _ClassVar[int]
    ARRIVAL_TIME_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_SEATS_FIELD_NUMBER: _ClassVar[int]
    id: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    price: float
    available_seats: int
    def __init__(self, id: _Optional[str] = ..., origin: _Optional[str] = ..., destination: _Optional[str] = ..., departure_time: _Optional[str] = ..., arrival_time: _Optional[str] = ..., price: _Optional[float] = ..., available_seats: _Optional[int] = ...) -> None: ...

class Seat(_message.Message):
    __slots__ = ("id", "flight_id", "seat_number", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    FLIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    SEAT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    flight_id: str
    seat_number: str
    status: str
    def __init__(self, id: _Optional[str] = ..., flight_id: _Optional[str] = ..., seat_number: _Optional[str] = ..., status: _Optional[str] = ...) -> None: ...

class ErrorResponse(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: int
    message: str
    def __init__(self, code: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...
