from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from excelify._cell import Cell
    from excelify._excelframe import CellMapping


class CellExpr(ABC):
    def __init__(self):
        self._last_value = None

    @property
    @abstractmethod
    def dependencies(self) -> list["Cell"]:
        raise NotImplementedError

    @abstractmethod
    def to_formula(self, mapping: "CellMapping") -> str:
        raise NotImplementedError

    @abstractmethod
    def compute(self) -> None:
        raise NotImplementedError

    @property
    def last_value(self) -> Any:
        return self._last_value

    def __truediv__(self, other) -> "CellExpr":
        from excelify._cell import Cell

        if isinstance(other, Cell):
            other = other.cell_expr
        return Div(self, other)

    def __neg__(self) -> "CellExpr":
        return Neg(self)


class Empty(CellExpr):
    def __init__(self):
        super().__init__()

    @property
    def dependencies(self) -> list["Cell"]:
        return []

    def to_formula(self, mapping: "CellMapping") -> str:
        return ""

    def compute(self) -> None:
        # TODO: Revisit this behavior.
        self._last_value = 0


class Constant(CellExpr):
    def __init__(self, value: int | float | str):
        super().__init__()
        self.value = value

    @property
    def dependencies(self) -> list["Cell"]:
        return []

    def to_formula(self, mapping: "CellMapping") -> str:
        return str(self.value)

    def compute(self) -> None:
        self._last_value = self.value


class CellRef(CellExpr):
    def __init__(self, cell_ref: "Cell"):
        super().__init__()
        self._cell_ref = cell_ref

    @property
    def dependencies(self) -> list["Cell"]:
        return [self._cell_ref]

    def to_formula(self, mapping: "CellMapping") -> str:
        return mapping[self._cell_ref.element]

    def compute(self) -> None:
        self._last_value = self._cell_ref.last_value


class Mult(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list["Cell"]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: "CellMapping") -> str:
        return f"""({self._left_cell_expr.to_formula(mapping)} * {
            self._right_cell_expr.to_formula(mapping)
        })"""

    def compute(self) -> None:
        self._left_cell_expr.compute()
        self._right_cell_expr.compute()
        self._last_value = (
            self._left_cell_expr.last_value * self._right_cell_expr.last_value
        )


class Add(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list["Cell"]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: "CellMapping") -> str:
        return f"""({self._left_cell_expr.to_formula(mapping)} + {
            self._right_cell_expr.to_formula(mapping)
        })"""

    def compute(self) -> None:
        self._left_cell_expr.compute()
        self._right_cell_expr.compute()
        self._last_value = (
            self._left_cell_expr.last_value + self._right_cell_expr.last_value
        )


class Div(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list["Cell"]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: "CellMapping") -> str:
        return f"""({self._left_cell_expr.to_formula(mapping)} / {
            self._right_cell_expr.to_formula(mapping)
        })"""

    def compute(self) -> None:
        self._left_cell_expr.compute()
        self._right_cell_expr.compute()
        try:
            self._last_value = (
                self._left_cell_expr.last_value / self._right_cell_expr.last_value
            )
        except ZeroDivisionError:
            self._last_value = np.inf


class Sub(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list["Cell"]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: "CellMapping") -> str:
        return f"""({self._left_cell_expr.to_formula(mapping)} - {
            self._right_cell_expr.to_formula(mapping)
        })"""

    def compute(self) -> None:
        self._left_cell_expr.compute()
        self._right_cell_expr.compute()
        self._last_value = (
            self._left_cell_expr.last_value - self._right_cell_expr.last_value
        )


class Neg(CellExpr):
    def __init__(self, expr: CellExpr):
        super().__init__()
        self._expr = expr

    @property
    def dependencies(self) -> list["Cell"]:
        return self._expr.dependencies

    def to_formula(self, mapping: "CellMapping") -> str:
        return f"(-{self._expr.to_formula(mapping)})"

    def compute(self) -> None:
        self._expr.compute()
        self._last_value = -self._expr.last_value
