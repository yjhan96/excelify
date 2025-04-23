from __future__ import annotations

from typing import TYPE_CHECKING, Any

from excelify._cell_expr import CellExpr, Constant
from excelify._types import RawInput

if TYPE_CHECKING:
    from excelify._excelframe import CellMapping, Element


class Cell:
    def __init__(self, element: Element, cell_expr: CellExpr):
        self._element = element
        self.cell_expr = cell_expr

    def to_formula(self, mapping: "CellMapping") -> str:
        return self.cell_expr.to_formula(mapping)

    @property
    def element(self) -> Element:
        return self._element

    @property
    def dependencies(self) -> list["Cell"]:
        return self.cell_expr.dependencies

    def compute(self) -> None:
        return self.cell_expr.compute()

    @property
    def last_value(self) -> Any:
        return self.cell_expr.last_value

    @classmethod
    def _resolve_to_cell_expr(cls, value: Cell | RawInput | CellExpr) -> CellExpr:
        if isinstance(value, Cell):
            return value.cell_expr
        elif isinstance(value, RawInput):
            return Constant(value)
        elif isinstance(value, CellExpr):
            return value
        else:
            raise ValueError(f"{value} has type {type(value)}, which isn't supported.'")

    def __truediv__(self, other: Cell | RawInput | CellExpr) -> CellExpr:
        other_resolved = Cell._resolve_to_cell_expr(other)
        return self.cell_expr / other_resolved

    def __neg__(self) -> CellExpr:
        return -self.cell_expr

    def __add__(self, other: Cell | RawInput | CellExpr) -> CellExpr:
        other_resolved = Cell._resolve_to_cell_expr(other)
        return self.cell_expr + other_resolved

    def __radd__(self, other: Cell | RawInput | CellExpr) -> CellExpr:
        other_resolved = Cell._resolve_to_cell_expr(other)
        return other_resolved + self.cell_expr

    def __mul__(self, other: Cell | RawInput | CellExpr) -> CellExpr:
        other_resolved = Cell._resolve_to_cell_expr(other)
        return self.cell_expr * other_resolved
