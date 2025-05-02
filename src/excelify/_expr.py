from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from excelify._cell import Cell
from excelify._cell_expr import (
    Add,
    CellExpr,
    CellRef,
    Constant,
    Div,
    Invalid,
    Mult,
    Neg,
    Sub,
)
from excelify._element import Element

if TYPE_CHECKING:
    from excelify._cell import Cell
    from excelify._excelframe import ExcelFrame


class Expr(ABC):
    def __init__(self):
        self._name = None

    def create_cell(self, df: "ExcelFrame", idx: int) -> Cell:
        return Cell(Element(df.id, str(self), idx), self.get_cell_expr(df, idx))

    @abstractmethod
    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        raise NotImplementedError

    @abstractmethod
    def _fallback_repr(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        if self._name is not None:
            return self._name
        else:
            return self._fallback_repr()

    def alias(self, name: str) -> "Expr":
        self._name = name
        return self

    def __mul__(self, other) -> "Expr":
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return MultCol(self, other)

    def __add__(self, other) -> "Expr":
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return AddCol(self, other)

    def __radd__(self, other) -> "Expr":
        return self + other

    def __truediv__(self, other) -> "Expr":
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return DivCol(self, other)

    def __sub__(self, other) -> "Expr":
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return SubCol(self, other)

    def __neg__(self) -> "Expr":
        return NegCol(self)


class ConstantExpr(Expr):
    def __init__(self, value: int | float):
        super().__init__()
        self._value = value

    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        return Constant(self._value)

    def _fallback_repr(self) -> str:
        return str(self._value)


class SingleCellExpr(Expr):
    def __init__(self, cell: Cell):
        super().__init__()
        self._cell = cell

    def get_cell_expr(self, df, idx) -> CellExpr:
        return self._cell.cell_expr

    def _fallback_repr(self) -> str:
        return f"{self._cell} Cell Expr"


class Col(Expr):
    def __init__(self, col_name: str, *, offset: int = 0):
        super().__init__()
        self._col_name = col_name
        self._offset = offset

    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        cells = df[self._col_name]
        adjusted_idx = idx + self._offset
        if adjusted_idx < 0 or adjusted_idx >= len(cells):
            return Invalid()
        else:
            return CellRef(df[self._col_name][adjusted_idx])

    def _fallback_repr(self) -> str:
        return f"Ref({self._col_name})"

    def prev(self, offset: int) -> "Col":
        return Col(self._col_name, offset=-offset)

    def next(self, offset: int) -> "Col":
        return Col(self._col_name, offset=offset)


def col(col_name: str, offset: int = 0):
    return Col(col_name, offset=offset)


class MultCol(Expr):
    def __init__(self, left_expr: Expr, right_expr: Expr):
        super().__init__()
        self._left_expr = left_expr
        self._right_expr = right_expr

    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        left_cell_expr = self._left_expr.get_cell_expr(df, idx)
        right_cell_expr = self._right_expr.get_cell_expr(df, idx)
        return Mult(left_cell_expr, right_cell_expr)

    def _fallback_repr(self) -> str:
        return f"Mult({self._left_expr}, {self._right_expr})"


class AddCol(Expr):
    def __init__(self, left_expr: Expr, right_expr: Expr):
        super().__init__()
        self._left_expr = left_expr
        self._right_expr = right_expr

    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        left_cell_expr = self._left_expr.get_cell_expr(df, idx)
        right_cell_expr = self._right_expr.get_cell_expr(df, idx)
        return Add(left_cell_expr, right_cell_expr)

    def _fallback_repr(self) -> str:
        return f"Add({self._left_expr}, {self._right_expr})"


class SubCol(Expr):
    def __init__(self, left_expr: Expr, right_expr: Expr):
        super().__init__()
        self._left_expr = left_expr
        self._right_expr = right_expr

    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        left_cell_expr = self._left_expr.get_cell_expr(df, idx)
        right_cell_expr = self._right_expr.get_cell_expr(df, idx)
        return Sub(left_cell_expr, right_cell_expr)

    def _fallback_repr(self) -> str:
        return f"Sub({self._left_expr}, {self._right_expr})"


class DivCol(Expr):
    def __init__(self, left_expr: Expr, right_expr: Expr):
        super().__init__()
        self._left_expr = left_expr
        self._right_expr = right_expr

    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        left_cell_expr = self._left_expr.get_cell_expr(df, idx)
        right_cell_expr = self._right_expr.get_cell_expr(df, idx)
        return Div(left_cell_expr, right_cell_expr)

    def _fallback_repr(self) -> str:
        return f"Div({self._left_expr}, {self._right_expr})"


class NegCol(Expr):
    def __init__(self, expr: Expr):
        super().__init__()
        self._expr = expr

    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        expr = self._expr.get_cell_expr(df, idx)
        return Neg(expr)

    def _fallback_repr(self) -> str:
        return f"Neg({self._expr})"
