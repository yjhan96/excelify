from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Any
import polars as pl
from pathlib import Path
from xlsxwriter import Workbook

from excelify._html import NotebookFormatter

RawInput = dict
Element = namedtuple("Element", ["col_name", "idx"])


class CellExpr(ABC):
    def __init__(self, element: Element):
        self.element = element
        self._last_value = None

    @property
    @abstractmethod
    def dependencies(self) -> list["CellExpr"]:
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


class Constant(CellExpr):
    def __init__(self, element: Element, value: int | float):
        super().__init__(element)
        self.value = value

    @property
    def dependencies(self) -> list[CellExpr]:
        return []

    def to_formula(self, _mapping: "CellMapping") -> str:
        return str(self.value)

    def compute(self) -> None:
        self._last_value = self.value


class CellRef(CellExpr):
    def __init__(self, element: Element, ref_cell: CellExpr):
        super().__init__(element)
        self._ref_cell = ref_cell

    @property
    def dependencies(self) -> list[CellExpr]:
        return [self._ref_cell]

    def to_formula(self, mapping: "CellMapping") -> str:
        return f"={mapping[self._ref_cell.element]}"

    def compute(self) -> None:
        self._last_value = self._ref_cell.last_value


class Expr(ABC):
    def __init__(self):
        self._name = None

    @abstractmethod
    def cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        raise NotImplementedError

    @abstractmethod
    def _fallback_repr(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        if self._name is not None:
            return self._name
        else:
            self._fallback_repr()

    def alias(self, name: str) -> "Expr":
        self._name = name
        return self


class Col(Expr):
    def __init__(self, col_name: str):
        super().__init__()
        self._col_name = col_name

    def cell_expr(self, df: "ExcelFrame", idx: int) -> CellExpr:
        return CellRef((self._name, idx), df[self._col_name][idx])

    def _fallback_repr(self) -> str:
        return f"Ref({self._col_name})"


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


def _topological_sort(
    cells: list[CellExpr],
) -> list[CellExpr]:
    visited = set()
    result = []

    def _sort_deps(cell_expr: CellExpr, result, visited):
        element = cell_expr.element
        visited.add(element)
        for dep in cell_expr.dependencies:
            if dep.element not in visited:
                _sort_deps(dep, result, visited)
        result.append(cell_expr)

    for cell_expr in cells:
        element = cell_expr.element
        if element in visited:
            continue
        _sort_deps(cell_expr, result, visited)

    return result


class ExcelFrame:
    def __init__(self, input: RawInput):
        self._input = {
            key: [
                Constant((key, i), value) if not isinstance(value, CellExpr) else value
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
            for i, (key, exprs) in enumerate(self._input.items()):
                worksheet.write(i, 0, key)
                for j, expr in enumerate(exprs):
                    worksheet.write(i, j + 1, expr.to_formula(mapping))

    def with_column(self, expr: Expr) -> "ExcelFrame":
        height = self.height
        self._input[str(expr)] = [expr.cell_expr(self, i) for i in range(height)]
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
                key: [Constant(value.element, value.last_value) for value in values]
                for key, values in self._input.items()
            }
        )
