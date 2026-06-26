import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SearchRequest(_message.Message):
    __slots__ = ("origin", "destination", "date")
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    origin: str
    destination: str
    date: str
    def __init__(self, origin: _Optional[str] = ..., destination: _Optional[str] = ..., date: _Optional[str] = ...) -> None: ...

class SearchResponse(_message.Message):
    __slots__ = ("flights",)
    FLIGHTS_FIELD_NUMBER: _ClassVar[int]
    flights: _containers.RepeatedCompositeFieldContainer[_common_pb2.Flight]
    def __init__(self, flights: _Optional[_Iterable[_Union[_common_pb2.Flight, _Mapping]]] = ...) -> None: ...
