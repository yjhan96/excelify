import uuid
from typing import Iterable

from excelify._cell import Cell
from excelify._cell_expr import CellExpr, Constant
from excelify._element import Element
from excelify._types import RawInput


class Column:
    def __init__(self, id: uuid.UUID, key: str, values: Iterable[Cell | RawInput]):
        self._id = id
        self._values = [
            (
                Cell(Element(id, key, i), Constant(value))
                if not isinstance(value, Cell)
                else value
            )
            for i, value in enumerate(values)
        ]
        self._key = key

    def __getitem__(self, idx: int) -> Cell:
        return self._values[idx]

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def _maybe_copy_on_write(self, idx):
        if self._values[idx].element != Element(self._id, self._key, idx):
            prev_cell = self._values[idx]
            self._values[idx] = Cell(
                Element(self._id, self._key, idx),
                prev_cell.cell_expr,
                attributes=prev_cell.attributes,
            )

    def __setitem__(self, idx: int, value: RawInput | CellExpr):
        if isinstance(value, RawInput):
            value = Constant(value)

        self._maybe_copy_on_write(idx)
        self._values[idx].set_expr(value)

    def set_attributes(self, attrs: dict) -> None:
        for idx in range(len(self._values)):
            self._maybe_copy_on_write(idx)
            self._values[idx].set_attributes(attrs)
