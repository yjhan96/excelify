from __future__ import annotations

from typing import TYPE_CHECKING, Any

from excelify._cell_expr import CellExpr

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

    def __truediv__(self, other) -> CellExpr:
        if isinstance(other, Cell):
            other = other.cell_expr
        return self.cell_expr / other

    def __neg__(self) -> CellExpr:
        return -self.cell_expr
