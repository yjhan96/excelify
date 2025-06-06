from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping

from excelify._cell_expr import CellExpr, Constant
from excelify._types import RawInput

if TYPE_CHECKING:
    from excelify._excelframe import CellMapping, Element
    from excelify._styler import Styler


def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


class Cell:
    def __init__(
        self,
        element: Element,
        cell_expr: CellExpr,
        *,
        attributes: dict | None = None,
        is_editable: bool = False,
    ):
        self._element = element
        self.cell_expr = cell_expr
        if attributes is None:
            self._attributes = {}
        else:
            self._attributes = attributes
        self._is_editable = is_editable
        self._last_value = None

    def to_formula(
        self,
        mapping: CellMapping,
        *,
        style: Styler | None = None,
        raise_if_missing: bool = True,
    ) -> str:
        value = self.cell_expr.to_formula(mapping, raise_if_missing=raise_if_missing)
        if _is_float(value):
            value = f"{float(value):,.2f}"

        if style is not None:
            return style.apply_value(self, value)
        else:
            return value

    @property
    def element(self) -> Element:
        return self._element

    @property
    def dependencies(self) -> list[Cell]:
        return self.cell_expr.dependencies

    @property
    def is_editable(self) -> bool:
        return self._is_editable

    @is_editable.setter
    def is_editable(self, value: bool) -> None:
        self._is_editable = value

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        self.cell_expr = self.cell_expr.update_cell_refs(ref_map)

    def compute(self) -> None:
        self._last_value = self.cell_expr.compute()

    def set_expr(self, cell_expr) -> None:
        self.cell_expr = cell_expr

    @property
    def last_value(self) -> Any:
        return self._last_value

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

    def set_attributes(self, attrs: dict) -> None:
        self._attributes = attrs

    @property
    def attributes(self) -> dict:
        return self._attributes

    def __repr__(self):
        return str(self._element)
