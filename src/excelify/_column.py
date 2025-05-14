from __future__ import annotations

import uuid
from typing import Iterable

from excelify._cell import Cell
from excelify._cell_expr import CellExpr, Constant
from excelify._element import Element
from excelify._types import RawInput


class Column:
    def __init__(
        self, id: uuid.UUID, key: str, values: Iterable[Cell | RawInput | CellExpr]
    ):
        self._id = id
        self._values: list[Cell] = []
        for i, value in enumerate(values):
            cell: Cell
            if isinstance(value, RawInput):
                cell = Cell(Element(id, key, i), Constant(value))
            elif isinstance(value, Cell):
                cell = Cell(
                    Element(id, key, i),
                    value.cell_expr,
                    attributes=value.attributes,
                    is_editable=value.is_editable,
                )
            else:
                cell = Cell(Element(id, key, i), value)
            self._values.append(cell)
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
        self._values[idx].set_expr(value)

    def set_attributes(self, attrs: dict) -> None:
        for cell in self._values:
            cell.set_attributes(attrs)

    def extend(self, other: Column) -> None:
        self._values.extend(other._values)

    @property
    def key(self) -> str:
        return self._key


class ColumnAutocompleter:
    def __init__(self, columns: Iterable[str]):
        self._columns = columns

        for col_name in self._columns:
            invalid_chars = [" ", "-", "(", ")", ","]
            revised_col_name = col_name
            for c in invalid_chars:
                revised_col_name = revised_col_name.replace(c, "_")
            revised_col_name = revised_col_name.replace("%", "percent")
            revised_col_name = revised_col_name.replace("&", "and")
            if hasattr(self, revised_col_name):
                raise ValueError(
                    "Column named collided during revision: "
                    f"{col_name} vs. {getattr(self, revised_col_name)}."
                )
            setattr(self, revised_col_name, col_name)
