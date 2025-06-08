from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Self

from excelify._cell import Cell
from excelify._cell_expr import (
    Add,
    AverageCellsRef,
    CellExpr,
    CellRef,
    Constant,
    Div,
    Invalid,
    Mult,
    Neg,
    Pow,
    Sub,
    SumCellsRef,
)
from excelify._types import RawInput

if TYPE_CHECKING:
    from excelify._cell import Cell
    from excelify._excelframe import ExcelFrame


class Expr(ABC):
    """An abstract class that represents a column expression. It'll be evaluated
    across the row when it's applied to the ExcelFrame.

    You can apply arithmetic operations to the expression directly.

    Example:
        ```pycon
        >>> import excelify as el
        >>> df = el.ExcelFrame({"x": [1, 2, 3]})
        >>> df = df.with_columns(
        ...     (el.col("x") * el.col("x")).alias("x_squared"),
        ...     (el.col("x") / 2).alias("x_div_2")
        ... )
        >>> df
        shape: (3, 3)
        +---+-------+---------------+-------------+
        |   | x (A) | x_squared (B) | x_div_2 (C) |
        +---+-------+---------------+-------------+
        | 1 | 1.00  |   (A1 * A1)   |  (A1 / 2)   |
        | 2 | 2.00  |   (A2 * A2)   |  (A2 / 2)   |
        | 3 | 3.00  |   (A3 * A3)   |  (A3 / 2)   |
        +---+-------+---------------+-------------+

        ```
    """

    def __init__(self):
        self._name = None

    @abstractmethod
    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        raise NotImplementedError

    @abstractmethod
    def _fallback_repr(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        if self._name is not None:
            return self._name
        else:
            return self._fallback_repr()

    def alias(self, name: str) -> Self:
        """Name the column for the given expression.

        Arguments:
            name: Name of the column

        Returns:
            self with name modified.
        """
        self._name = name
        return self

    def __mul__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return MultCol(self, other)

    def __rmul__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return MultCol(other, self)

    def __add__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return AddCol(self, other)

    def __radd__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return AddCol(other, self)

    def __truediv__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return DivCol(self, other)

    def __rtruediv__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return DivCol(other, self)

    def __sub__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return SubCol(self, other)

    def __rsub__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return SubCol(other, self)

    def __neg__(self) -> Expr:
        return NegCol(self)

    def __pow__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return PowCol(self, other)

    def __rpow__(self, other) -> Expr:
        if isinstance(other, int) or isinstance(other, float):
            other = ConstantExpr(other)

        assert isinstance(other, Expr)
        return PowCol(other, self)


class ConstantExpr(Expr):
    def __init__(self, value: int | float):
        super().__init__()
        self._value = value

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
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
    def __init__(
        self, col_name: str, *, from_: ExcelFrame | None = None, offset: int = 0
    ):
        super().__init__()
        self._col_name = col_name
        self._offset = offset
        self.from_ = from_

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        from_df = self.from_ if self.from_ is not None else df
        cells = from_df[self._col_name]
        adjusted_idx = idx + self._offset
        if adjusted_idx < 0 or adjusted_idx >= len(cells):
            return Invalid()
        else:
            return CellRef(cells[adjusted_idx])

    def _fallback_repr(self) -> str:
        return f"Ref({self._col_name})"

    def prev(self, offset: int) -> "Col":
        return Col(self._col_name, offset=-offset)

    def next(self, offset: int) -> "Col":
        return Col(self._col_name, offset=offset)


def col(col_name: str, *, from_: ExcelFrame | None = None, offset: int = 0):
    """`Expresses a reference to the cell in a specified column.

    Example:
        ```pycon
        >>> import excelify as el
        >>> df = el.ExcelFrame({"x": [1, 2], "y": [3, 4]})
        >>> df = df.with_columns((el.col("x") + el.col("y")).alias("z"))
        >>> df
        shape: (2, 3)
        +---+-------+-------+-----------+
        |   | x (A) | y (B) |   z (C)   |
        +---+-------+-------+-----------+
        | 1 | 1.00  | 3.00  | (A1 + B1) |
        | 2 | 2.00  | 4.00  | (A2 + B2) |
        +---+-------+-------+-----------+

        ```

    Arguments:
        col_name: Name of the column
        from_: Which `ExcelFrame` to refer to. If it's None, it'll refer to
            the column of its own ExcelFrame.
        offset: Relative row offset to refer to different rows.
    """
    return Col(col_name, from_=from_, offset=offset)


class FixedCell(Expr):
    def __init__(self, cell: Cell):
        super().__init__()
        self._cell = cell

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        return CellRef(self._cell)

    def _fallback_repr(self) -> str:
        return f"FixedRef({self._cell})"


def cell(cell: Cell):
    """Expresses a fixed cell location. A fixed cell will be broadcasted across the row."""
    return FixedCell(cell)


class LitColumn(Expr):
    def __init__(self, column: list[RawInput]):
        super().__init__()
        self._column = column

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        return Constant(self._column[idx])

    def _fallback_repr(self) -> str:
        raise ValueError("Impossible to reach!")


def lit(value: RawInput | list[RawInput]) -> Expr:
    """Expresses a constant value across the rows.

    Example:
        ```pycon
        >>> import excelify as el
        >>> df = el.ExcelFrame.empty(columns=["x", "y"], height=2)
        >>> df = df.with_columns(
        ...     el.lit(0).alias("x"),
        ...     el.lit([1, 2]).alias("y")
        ... )
        >>> df
        shape: (2, 2)
        +---+-------+-------+
        |   | x (A) | y (B) |
        +---+-------+-------+
        | 1 | 0.00  | 1.00  |
        | 2 | 0.00  | 2.00  |
        +---+-------+-------+

        ```

    Arguments:
        value: A constant value to put in the cell. If it's a scalar value,
            the value will be broadcasted.
    """
    if isinstance(value, int) or isinstance(value, float):
        return ConstantExpr(value)
    elif isinstance(value, list):
        return LitColumn(value)
    else:
        raise ValueError(f"Invalid type of value: {value} ({type(value)})")


class MultCol(Expr):
    def __init__(self, left_expr: Expr, right_expr: Expr):
        super().__init__()
        self._left_expr = left_expr
        self._right_expr = right_expr

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
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

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
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

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
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

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        left_cell_expr = self._left_expr.get_cell_expr(df, idx)
        right_cell_expr = self._right_expr.get_cell_expr(df, idx)
        return Div(left_cell_expr, right_cell_expr)

    def _fallback_repr(self) -> str:
        return f"Div({self._left_expr}, {self._right_expr})"


class NegCol(Expr):
    def __init__(self, expr: Expr):
        super().__init__()
        self._expr = expr

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        expr = self._expr.get_cell_expr(df, idx)
        return Neg(expr)

    def _fallback_repr(self) -> str:
        return f"Neg({self._expr})"


class PowCol(Expr):
    def __init__(self, left_expr: Expr, right_expr: Expr):
        super().__init__()
        self._left_expr = left_expr
        self._right_expr = right_expr

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        left_cell_expr = self._left_expr.get_cell_expr(df, idx)
        right_cell_expr = self._right_expr.get_cell_expr(df, idx)
        return Pow(left_cell_expr, right_cell_expr)

    def _fallback_repr(self) -> str:
        return f"Exp({self._left_expr}, {self._right_expr})"


class Map(Expr):
    def __init__(self, fn: Callable[[int], CellExpr | RawInput | Expr]):
        super().__init__()
        self._fn = fn

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        res = self._fn(idx)
        if isinstance(res, RawInput):
            return Constant(res)
        elif isinstance(res, Expr):
            return res.get_cell_expr(df, idx)
        else:
            return res

    def _fallback_repr(self) -> str:
        raise ValueError(f"Please provide a name of the map column!: {self._fn=}")


def map(fn: Callable[[int], CellExpr | RawInput | Expr]) -> Map:
    """Creates an expression based on the given function `fn` per row.

    Example:
        ```pycon
        >>> import excelify as el
        >>> df = el.ExcelFrame.empty(columns=["x", "y"], height=2)
        >>> df = df.with_columns(
        ...     el.map(lambda idx: idx + 1).alias("x"),
        ...     el.map(lambda idx: idx * 2).alias("y")
        ... )
        >>> df
        shape: (2, 2)
        +---+-------+-------+
        |   | x (A) | y (B) |
        +---+-------+-------+
        | 1 | 1.00  | 0.00  |
        | 2 | 2.00  | 2.00  |
        +---+-------+-------+

        ```
    Arguments:
        fn: A callable that takes row index and returns an expression for
            the row.

    Returns:
        A `Map` expression.
    """
    return Map(fn)


class SumCol(Expr):
    def __init__(self, col_name: str, *, from_: ExcelFrame | None = None):
        super().__init__()
        self._col_name = col_name
        self.from_ = from_

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        from_df = self.from_ if self.from_ is not None else df
        column = [cell for cell in from_df[self._col_name]]
        return SumCellsRef(column)

    def _fallback_repr(self) -> str:
        return f"Sum({self._col_name})"


def sum(col_name: str, *, from_: ExcelFrame | None = None):
    """Create an expression that represents the sum of the column. The value
    will be broadcasted across the row.

    Example:
        ```pycon
        >>> import excelify as el
        >>> df = el.ExcelFrame({"x": [1, 2, 3]})
        >>> df = df.with_columns(el.sum("x").alias("x_sum"))
        >>> df
        shape: (3, 2)
        +---+-------+------------+
        |   | x (A) | x_sum (B)  |
        +---+-------+------------+
        | 1 | 1.00  | SUM(A1:A3) |
        | 2 | 2.00  | SUM(A1:A3) |
        | 3 | 3.00  | SUM(A1:A3) |
        +---+-------+------------+
        >>> df.evaluate()
        shape: (3, 2)
        +---+-------+-----------+
        |   | x (A) | x_sum (B) |
        +---+-------+-----------+
        | 1 | 1.00  |   6.00    |
        | 2 | 2.00  |   6.00    |
        | 3 | 3.00  |   6.00    |
        +---+-------+-----------+

        ```

    Arguments:
        col_name: Column name
        from_: An ExcelFrame to refer to. If None, it'll refer to itself.
    """
    return SumCol(col_name, from_=from_)


class AverageCol(Expr):
    def __init__(self, col_name: str, *, from_: ExcelFrame | None = None):
        super().__init__()
        self._col_name = col_name
        self.from_ = from_

    def get_cell_expr(self, df: ExcelFrame, idx: int) -> CellExpr:
        from_df = self.from_ if self.from_ is not None else df
        column = [cell for cell in from_df[self._col_name]]
        return AverageCellsRef(column)

    def _fallback_repr(self) -> str:
        return f"Average({self._col_name})"


def average(col_name: str, *, from_: ExcelFrame | None = None):
    """Create an expression that represents the average of the column. The value
    will be broadcasted across the row.

    Example:
        ```pycon
        >>> import excelify as el
        >>> df = el.ExcelFrame({"x": [1, 2, 3]})
        >>> df = df.with_columns(el.average("x").alias("x_sum"))
        >>> df
        shape: (3, 2)
        +---+-------+----------------+
        |   | x (A) |   x_sum (B)    |
        +---+-------+----------------+
        | 1 | 1.00  | AVERAGE(A1:A3) |
        | 2 | 2.00  | AVERAGE(A1:A3) |
        | 3 | 3.00  | AVERAGE(A1:A3) |
        +---+-------+----------------+
        >>> df.evaluate()
        shape: (3, 2)
        +---+-------+-----------+
        |   | x (A) | x_sum (B) |
        +---+-------+-----------+
        | 1 | 1.00  |   2.00    |
        | 2 | 2.00  |   2.00    |
        | 3 | 3.00  |   2.00    |
        +---+-------+-----------+

        ```

    Arguments:
        col_name: Column name
        from_: An ExcelFrame to refer to. If None, it'll refer to itself.
    """
    return AverageCol(col_name, from_=from_)
