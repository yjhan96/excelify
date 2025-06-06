from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Mapping

import numpy as np

from excelify._element import Element

if TYPE_CHECKING:
    from excelify._cell import Cell
    from excelify._excelframe import CellMapping


class InvalidCellException(Exception):
    pass


class CellExpr(ABC):
    @property
    @abstractmethod
    def dependencies(self) -> list[Cell]:
        raise NotImplementedError

    @abstractmethod
    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        raise NotImplementedError

    @abstractmethod
    def compute(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def is_primitive(self) -> bool:
        raise NotImplementedError

    def __truediv__(self, other: CellExpr) -> CellExpr:
        return Div(self, other)

    def __neg__(self) -> CellExpr:
        return Neg(self)

    def __add__(self, other: CellExpr) -> CellExpr:
        return Add(self, other)

    def __sub__(self, other: CellExpr) -> CellExpr:
        return Sub(self, other)

    def __mul__(self, other: CellExpr) -> CellExpr:
        return Mult(self, other)

    def __pow__(self, other: CellExpr) -> CellExpr:
        return Pow(self, other)

    @abstractmethod
    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        raise NotImplementedError


class Empty(CellExpr):
    def __init__(self):
        super().__init__()

    @property
    def dependencies(self) -> list[Cell]:
        return []

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        return ""

    def compute(self) -> Any:
        return 0

    def is_primitive(self) -> bool:
        return True

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        return self


class Invalid(CellExpr):
    def __init__(self):
        super().__init__()

    @property
    def dependencies(self) -> list[Cell]:
        return []

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        raise InvalidCellException("Invalid cell!")

    def compute(self) -> Any:
        return None

    def is_primitive(self) -> bool:
        return True

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        return self


class Constant(CellExpr):
    def __init__(self, value: int | float | str):
        super().__init__()
        self.value = value

    @property
    def dependencies(self) -> list[Cell]:
        return []

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        return str(self.value)

    def compute(self) -> Any:
        return self.value

    def is_primitive(self) -> bool:
        return True

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        return self


def _get_cell_mapping(
    element: Element, mapping: CellMapping, raise_if_missing: bool
) -> str:
    if raise_if_missing or element in mapping:
        return mapping[element]
    else:
        _, col_name, idx = element
        return f"???:{col_name}:{idx}"


class CellRef(CellExpr):
    def __init__(self, cell_ref: Cell):
        super().__init__()
        self._cell_ref = cell_ref

    @property
    def dependencies(self) -> list[Cell]:
        return [self._cell_ref]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        return _get_cell_mapping(self._cell_ref.element, mapping, raise_if_missing)

    def compute(self) -> Any:
        return self._cell_ref.last_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        if self._cell_ref.element in ref_map:
            return CellRef(ref_map[self._cell_ref.element])
        else:
            return self


class SumCellsRef(CellExpr):
    def __init__(self, cells: list[Cell]):
        super().__init__()
        self._cells = cells

    @property
    def dependencies(self) -> list[Cell]:
        return [cell for cell in self._cells]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        from_cell = _get_cell_mapping(self._cells[0].element, mapping, raise_if_missing)
        to_cell = _get_cell_mapping(self._cells[-1].element, mapping, raise_if_missing)
        return f"SUM({from_cell}:{to_cell})"

    def compute(self) -> Any:
        values = [cell.last_value for cell in self._cells]

        if any(value is None for value in values):
            return None
        else:
            return sum(values)

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        if any(self._cells[i].element in ref_map for i in range(len(self._cells))):
            cells = []
            for i in range(len(self._cells)):
                if self._cells[i].element in ref_map:
                    cells.append(ref_map[self._cells[i].element])
                else:
                    cells.append(self._cells[i])
            return SumCellsRef(cells)
        else:
            return self


class AverageCellsRef(CellExpr):
    def __init__(self, cells: list[Cell]):
        super().__init__()
        self._cells = cells

    @property
    def dependencies(self) -> list[Cell]:
        return [cell for cell in self._cells]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        from_cell = _get_cell_mapping(self._cells[0].element, mapping, raise_if_missing)
        to_cell = _get_cell_mapping(self._cells[-1].element, mapping, raise_if_missing)
        return f"AVERAGE({from_cell}:{to_cell})"

    def compute(self) -> Any:
        values = [cell.last_value for cell in self._cells]

        if any(value is None for value in values):
            return None
        else:
            return sum(values) / len(values)

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        if any(self._cells[i].element in ref_map for i in range(len(self._cells))):
            cells = []
            for i in range(len(self._cells)):
                if self._cells[i].element in ref_map:
                    cells.append(ref_map[self._cells[i].element])
                else:
                    cells.append(self._cells[i])
            return SumCellsRef(cells)
        else:
            return self


class Mult(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            return f"({left_cell_formula} * {right_cell_formula})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            return left_value * right_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Mult(left_cell_expr, right_cell_expr)


class Add(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            return f"({left_cell_formula} + {right_cell_formula})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()
        if left_value is None or right_value is None:
            return None
        else:
            return left_value + right_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Add(left_cell_expr, right_cell_expr)


class Div(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            return f"({left_cell_formula} / {right_cell_formula})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            try:
                return left_value / right_value
            except ZeroDivisionError:
                return np.inf

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Div(left_cell_expr, right_cell_expr)


class Sub(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            return f"({left_cell_formula} - {right_cell_formula})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            return left_value - right_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Sub(left_cell_expr, right_cell_expr)


class Pow(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            return f"({left_cell_formula} ^ {right_cell_formula})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            return left_value**right_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Pow(left_cell_expr, right_cell_expr)


class Neg(CellExpr):
    def __init__(self, expr: CellExpr):
        super().__init__()
        self._expr = expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._expr.dependencies

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> str:
        try:
            return f"(-{self._expr.to_formula(mapping, raise_if_missing=raise_if_missing)})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> None:
        value = self._expr.compute()
        if value is None:
            return None
        else:
            return -value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        expr = self._expr.update_cell_refs(ref_map)
        if expr == self._expr:
            return self
        else:
            return Neg(expr)
