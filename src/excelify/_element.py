import uuid
from typing import NamedTuple


class Element(NamedTuple):
    id: uuid.UUID
    col_name: str
    idx: int
