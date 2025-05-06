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
    def __init__(self):
        self._last_value = None

    @property
    @abstractmethod
    def dependencies(self) -> list[Cell]:
        raise NotImplementedError

    @abstractmethod
    def to_formula(self, mapping: CellMapping) -> str:
        raise NotImplementedError

    @abstractmethod
    def compute(self) -> None:
        raise NotImplementedError

    @property
    def last_value(self) -> Any:
        return self._last_value

    @abstractmethod
    def is_primitive(self) -> bool:
        raise NotImplementedError

    def __truediv__(self, other: CellExpr) -> CellExpr:
        return Div(self, other)

    def __neg__(self) -> CellExpr:
        return Neg(self)

    def __add__(self, other: CellExpr) -> CellExpr:
        return Add(self, other)

    def __mul__(self, other: CellExpr) -> CellExpr:
        return Mult(self, other)

    @abstractmethod
    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        raise NotImplementedError


class Empty(CellExpr):
    def __init__(self):
        super().__init__()

    @property
    def dependencies(self) -> list[Cell]:
        return []

    def to_formula(self, mapping: CellMapping) -> str:
        return ""

    def compute(self) -> None:
        self._last_value = 0

    def is_primitive(self) -> bool:
        return True

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        return


class Invalid(CellExpr):
    def __init__(self):
        super().__init__()

    @property
    def dependencies(self) -> list[Cell]:
        return []

    def to_formula(self, mapping: CellMapping) -> str:
        raise InvalidCellException("Invalid cell!")

    def compute(self) -> None:
        self._last_value = None

    def is_primitive(self) -> bool:
        return True

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        return


class Constant(CellExpr):
    def __init__(self, value: int | float | str):
        super().__init__()
        self.value = value

    @property
    def dependencies(self) -> list[Cell]:
        return []

    def to_formula(self, mapping: CellMapping) -> str:
        return str(self.value)

    def compute(self) -> None:
        self._last_value = self.value

    def is_primitive(self) -> bool:
        return True

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        return


class CellRef(CellExpr):
    def __init__(self, cell_ref: Cell):
        super().__init__()
        self._cell_ref = cell_ref

    @property
    def dependencies(self) -> list[Cell]:
        return [self._cell_ref]

    def to_formula(self, mapping: CellMapping) -> str:
        return mapping[self._cell_ref.element]

    def compute(self) -> None:
        self._last_value = self._cell_ref.last_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        if self._cell_ref.element in ref_map:
            self._cell_ref = ref_map[self._cell_ref.element]


class Mult(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping) -> str:
        try:
            return f"""({self._left_cell_expr.to_formula(mapping)} * {
                self._right_cell_expr.to_formula(mapping)
            })"""
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> None:
        self._left_cell_expr.compute()
        self._right_cell_expr.compute()
        left_last_value = self._left_cell_expr.last_value
        right_last_value = self._right_cell_expr.last_value

        if left_last_value is None or right_last_value is None:
            self._last_value = None
        else:
            self._last_value = left_last_value * right_last_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        self._left_cell_expr.update_cell_refs(ref_map)
        self._right_cell_expr.update_cell_refs(ref_map)


class Add(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping) -> str:
        try:
            return f"""({self._left_cell_expr.to_formula(mapping)} + {
                self._right_cell_expr.to_formula(mapping)
            })"""
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> None:
        self._left_cell_expr.compute()
        self._right_cell_expr.compute()
        left_last_value = self._left_cell_expr.last_value
        right_last_value = self._right_cell_expr.last_value
        if left_last_value is None or right_last_value is None:
            self._last_value = None
        else:
            self._last_value = left_last_value + right_last_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        self._left_cell_expr.update_cell_refs(ref_map)
        self._right_cell_expr.update_cell_refs(ref_map)


class Div(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping) -> str:
        try:
            return f"""({self._left_cell_expr.to_formula(mapping)} / {
                self._right_cell_expr.to_formula(mapping)
            })"""
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> None:
        self._left_cell_expr.compute()
        self._right_cell_expr.compute()
        left_last_value = self._left_cell_expr.last_value
        right_last_value = self._right_cell_expr.last_value

        if left_last_value is None or right_last_value is None:
            self._last_value = None
        else:
            try:
                self._last_value = left_last_value / right_last_value
            except ZeroDivisionError:
                self._last_value = np.inf

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        self._left_cell_expr.update_cell_refs(ref_map)
        self._right_cell_expr.update_cell_refs(ref_map)


class Sub(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping) -> str:
        try:
            return f"""({self._left_cell_expr.to_formula(mapping)} - {
                self._right_cell_expr.to_formula(mapping)
            })"""
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> None:
        self._left_cell_expr.compute()
        self._right_cell_expr.compute()
        left_last_value = self._left_cell_expr.last_value
        right_last_value = self._right_cell_expr.last_value

        if left_last_value is None or right_last_value is None:
            self._last_value = None
        else:
            self._last_value = left_last_value - right_last_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        self._left_cell_expr.update_cell_refs(ref_map)
        self._right_cell_expr.update_cell_refs(ref_map)


class Neg(CellExpr):
    def __init__(self, expr: CellExpr):
        super().__init__()
        self._expr = expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._expr.dependencies

    def to_formula(self, mapping: CellMapping) -> str:
        try:
            return f"(-{self._expr.to_formula(mapping)})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> None:
        self._expr.compute()
        if self._expr.last_value is None:
            self._last_value = None
        else:
            self._last_value = -self._expr.last_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> None:
        self._expr.update_cell_refs(ref_map)
