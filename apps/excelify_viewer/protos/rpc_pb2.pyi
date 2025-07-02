from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReloadRequest(_message.Message):
    __slots__ = ("script_path",)
    SCRIPT_PATH_FIELD_NUMBER: _ClassVar[int]
    script_path: str
    def __init__(self, script_path: _Optional[str] = ...) -> None: ...

class ReloadResponse(_message.Message):
    __slots__ = ("table",)
    TABLE_FIELD_NUMBER: _ClassVar[int]
    table: _struct_pb2.Struct
    def __init__(self, table: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class GetSheetRequest(_message.Message):
    __slots__ = ("script_path",)
    SCRIPT_PATH_FIELD_NUMBER: _ClassVar[int]
    script_path: str
    def __init__(self, script_path: _Optional[str] = ...) -> None: ...

class GetSheetResponse(_message.Message):
    __slots__ = ("table",)
    TABLE_FIELD_NUMBER: _ClassVar[int]
    table: _struct_pb2.Struct
    def __init__(self, table: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class UpdateCellRequest(_message.Message):
    __slots__ = ("script_path", "pos", "value")
    SCRIPT_PATH_FIELD_NUMBER: _ClassVar[int]
    POS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    script_path: str
    pos: Position
    value: float
    def __init__(self, script_path: _Optional[str] = ..., pos: _Optional[_Union[Position, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class UpdateCellResponse(_message.Message):
    __slots__ = ("table",)
    TABLE_FIELD_NUMBER: _ClassVar[int]
    table: _struct_pb2.Struct
    def __init__(self, table: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class LoadFileRequest(_message.Message):
    __slots__ = ("script_path",)
    SCRIPT_PATH_FIELD_NUMBER: _ClassVar[int]
    script_path: str
    def __init__(self, script_path: _Optional[str] = ...) -> None: ...

class LoadFileResponse(_message.Message):
    __slots__ = ("table",)
    TABLE_FIELD_NUMBER: _ClassVar[int]
    table: _struct_pb2.Struct
    def __init__(self, table: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class SaveFileRequest(_message.Message):
    __slots__ = ("script_path", "file_path")
    SCRIPT_PATH_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    script_path: str
    file_path: str
    def __init__(self, script_path: _Optional[str] = ..., file_path: _Optional[str] = ...) -> None: ...

class SaveFileResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Position(_message.Message):
    __slots__ = ("row", "col")
    ROW_FIELD_NUMBER: _ClassVar[int]
    COL_FIELD_NUMBER: _ClassVar[int]
    row: int
    col: int
    def __init__(self, row: _Optional[int] = ..., col: _Optional[int] = ...) -> None: ...
