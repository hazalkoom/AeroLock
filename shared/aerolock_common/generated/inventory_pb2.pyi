import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AcquireLockRequest(_message.Message):
    __slots__ = ("flight_id", "seat_id")
    FLIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    SEAT_ID_FIELD_NUMBER: _ClassVar[int]
    flight_id: str
    seat_id: str
    def __init__(self, flight_id: _Optional[str] = ..., seat_id: _Optional[str] = ...) -> None: ...

class AcquireLockResponse(_message.Message):
    __slots__ = ("success", "token", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    token: str
    message: str
    def __init__(self, success: _Optional[bool] = ..., token: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class ConfirmBookingRequest(_message.Message):
    __slots__ = ("seat_id", "user_id", "token", "idempotency_key")
    SEAT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_KEY_FIELD_NUMBER: _ClassVar[int]
    seat_id: str
    user_id: str
    token: str
    idempotency_key: str
    def __init__(self, seat_id: _Optional[str] = ..., user_id: _Optional[str] = ..., token: _Optional[str] = ..., idempotency_key: _Optional[str] = ...) -> None: ...

class ConfirmBookingResponse(_message.Message):
    __slots__ = ("success", "booking_id", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    BOOKING_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    booking_id: str
    message: str
    def __init__(self, success: _Optional[bool] = ..., booking_id: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class ReleaseLockRequest(_message.Message):
    __slots__ = ("seat_id", "token")
    SEAT_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    seat_id: str
    token: str
    def __init__(self, seat_id: _Optional[str] = ..., token: _Optional[str] = ...) -> None: ...
