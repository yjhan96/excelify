from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, NamedTuple

import polars as pl
from xlsxwriter import Workbook

from excelify._html import NotebookFormatter

RawInput = dict


class Element(NamedTuple):
    col_name: str
    idx: int


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
    def __init__(self, value: int | float):
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
        self._last_value = (
            self._left_cell_expr.last_value / self._right_cell_expr.last_value
        )


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


class Expr(ABC):
    def __init__(self):
        self._name = None

    def create_cell(self, df: "ExcelFrame", idx: int) -> Cell:
        return Cell(Element(str(self), idx), self.get_cell_expr(df, idx))

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


class ConstantExpr(Expr):
    def __init__(self, value: int | float):
        super().__init__()
        self._value = value

    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        return Constant(self._value)

    def _fallback_repr(self) -> str:
        return str(self._value)


class Col(Expr):
    def __init__(self, col_name: str, offset: int = 0):
        super().__init__()
        self._col_name = col_name
        self._offset = offset

    def get_cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        cells = df[self._col_name]
        adjusted_idx = idx + self._offset
        if adjusted_idx < 0 or adjusted_idx >= len(cells):
            return Empty()
        else:
            return CellRef(df[self._col_name][adjusted_idx])

    def _fallback_repr(self) -> str:
        return f"Ref({self._col_name})"

    def prev(self, offset: int) -> "Col":
        return Col(self._col_name, -offset)

    def next(self, offset: int) -> "Col":
        return Col(self._col_name, offset)


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


class CellMapping:
    def __init__(self, columns: list | dict, start_pos: tuple[int, int]):
        if isinstance(columns, list):
            self._columns = {c: i for i, c in enumerate(columns)}
        else:
            assert isinstance(columns, dict)
            self._columns = columns
        self._start_pos = start_pos

    def _int_to_alpha(self, idx: int) -> str:
        num_alphabets = 26

        if idx == 0:
            return "A"
        result = []
        while idx > 0:
            rem = idx % num_alphabets
            result.append(chr(ord("A") + rem))
            idx = idx // num_alphabets
        return "".join(reversed(result))

    def __getitem__(self, element: Element) -> str:
        start_row, start_col = self._start_pos
        col_name, idx = element
        return f"{self._int_to_alpha(idx + start_col + 1)}{self._columns[col_name] + start_row + 1}"


def _topological_sort(cells: list[Cell]) -> list[Cell]:
    visited = set()
    result = []

    def _sort_deps(cell: Cell, result, visited):
        element = cell.element
        visited.add(element)
        for dep in cell.dependencies:
            if dep.element not in visited:
                _sort_deps(dep, result, visited)
        result.append(cell)

    for cell in cells:
        element = cell.element
        if element in visited:
            continue
        _sort_deps(cell, result, visited)

    return result


class ExcelFrame:
    def __init__(self, input: RawInput):
        self._input = {
            key: [
                (
                    Cell(Element(key, i), Constant(value))
                    if not isinstance(value, Cell)
                    else value
                )
                for i, value in enumerate(values)
            ]
            for key, values in input.items()
        }

    def __getitem__(self, idx_or_column: int | str):
        if isinstance(idx_or_column, int):
            # TODO: Come back to this.
            idx = idx_or_column
            return [series[idx] for series in self._input.values()]
        else:
            column = idx_or_column
            return self._input[column]

    @property
    def height(self) -> int:
        if self.width == 0:
            return 0
        return len(next(iter(self._input.values())))

    @property
    def width(self) -> int:
        return len(self._input)

    @property
    def shape(self) -> tuple[int, int]:
        return (self.height, self.width)

    @property
    def columns(self) -> list[str]:
        return list(self._input.keys())

    def _repr_html_(self):
        return "".join(NotebookFormatter(self).render())

    def write_excel(self, path: Path) -> None:
        mapping = CellMapping(self.columns, start_pos=(0, 0))
        with Workbook(path) as wb:
            worksheet = wb.add_worksheet()
            for i, (key, cells) in enumerate(self._input.items()):
                worksheet.write(i, 0, key)
                for j, cell in enumerate(cells):
                    worksheet.write(i, j + 1, f"={cell.to_formula(mapping)}")

    def with_column(self, expr: Expr) -> "ExcelFrame":
        height = self.height
        self._input[str(expr)] = [expr.create_cell(self, i) for i in range(height)]
        return self

    def to_html_val(self, r: int, c: int, mapping: CellMapping) -> str:
        cell_expr = self._input[self.columns[c]][r]
        return cell_expr.to_formula(mapping)

    def evaluate(self) -> "ExcelFrame":
        cells = [expr for exprs in self._input.values() for expr in exprs]

        sorted_cells = _topological_sort(cells)
        for cell in sorted_cells:
            cell.compute()

        return ExcelFrame(
            {
                key: [
                    Cell(value.element, Constant(value.last_value)) for value in values
                ]
                for key, values in self._input.items()
            }
        )
