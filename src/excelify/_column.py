from typing import Iterable

from excelify._cell import Cell
from excelify._cell_expr import CellExpr, Constant
from excelify._element import Element
from excelify._types import RawInput


class Column:
    def __init__(self, key: str, values: Iterable[Cell | RawInput]):
        self._values = [
            (
                Cell(Element(key, i), Constant(value))
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

    def __setitem__(self, idx: int, value: RawInput | CellExpr):
        if isinstance(value, RawInput):
            value = Constant(value)

        self._values[idx] = Cell(Element(self._key, idx), value)
