from __future__ import annotations

import uuid
from pathlib import Path
from typing import Iterable, Mapping, overload

import openpyxl

from excelify._cell import Cell
from excelify._column import Column
from excelify._element import Element
from excelify._expr import Expr
from excelify._html import NotebookFormatter
from excelify._types import RawInput


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
        _, col_name, idx = element
        return f"{self._int_to_alpha(idx + start_col)}{self._columns[col_name] + start_row}"


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
        if element not in visited:
            _sort_deps(cell, result, visited)

    return result


class ExcelFrame:
    def __init__(self, input: Mapping[str, Iterable[RawInput | Cell]]):
        self._id = uuid.uuid4()
        self._input = {
            key: Column(self._id, key, values) for key, values in input.items()
        }
        self._ordered_columns = list(self._input.keys())

    @overload
    def __getitem__(self, idx_or_column: int) -> Iterable[Cell]: ...

    @overload
    def __getitem__(self, idx_or_column: str) -> Column: ...

    def __getitem__(self, idx_or_column: int | str) -> Iterable[Cell] | Column:
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
        return self._ordered_columns

    @property
    def id(self) -> uuid.UUID:
        return self._id

    def _repr_html_(self):
        return "".join(NotebookFormatter(self).render())

    def to_excel(
        self,
        path: Path | str,
        *,
        start_pos: tuple[int, int] = (1, 1),
        write_values: bool = True,
    ) -> None:
        # Ideally, we'd like to write a function `of_excel` that will read
        # an excel file and create an ExcelFrame. However, this is slightly
        # nontrivial as we need to parse the formula and rewire the cells
        # in Python. Even though this isn't impossible, we defer it for now
        # and write two excel files, one with formulas and one wih values only.

        path = Path(path) if isinstance(path, str) else path
        mapping = CellMapping(self.columns, start_pos=start_pos)
        if path.exists():
            workbook = openpyxl.load_workbook(path)
        else:
            workbook = openpyxl.Workbook()
        worksheet = workbook.active
        assert worksheet is not None
        start_row, start_col = start_pos
        for i, col in enumerate(self._ordered_columns):
            cells = self._input[col]
            worksheet.cell(row=start_row + i, column=start_col).value = col
            start_offset = 1
            for j, cell in enumerate(cells):
                formula = cell.to_formula(mapping)
                if not cell.cell_expr.is_primitive():
                    formula = f"={formula}"
                worksheet.cell(
                    row=start_row + i, column=start_col + j + start_offset
                ).value = formula

        workbook.save(path)

        if write_values:
            file_name = path.name
            value_file_path = path.parent / (
                file_name.removesuffix(".xlsx") + "_value.xlsx"
            )
            self.evaluate().to_excel(
                value_file_path, start_pos=start_pos, write_values=False
            )

    def with_columns(self, *exprs: Expr) -> ExcelFrame:
        height = self.height
        for expr in exprs:
            col_name = str(expr)
            if col_name not in self._input:
                self._ordered_columns.append(col_name)
            self._input[col_name] = Column(
                self._id, col_name, [expr.create_cell(self, i) for i in range(height)]
            )
        return self

    def evaluate(self) -> ExcelFrame:
        cells = [cell for cells in self._input.values() for cell in cells]

        sorted_cells = _topological_sort(cells)
        for cell in sorted_cells:
            cell.compute()

        return ExcelFrame(
            {
                key: [value.last_value for value in values]
                for key, values in self._input.items()
            }
        )

    def transpose(
        self,
        *,
        include_header: bool = False,
        header_name: str = "column",
        column_names: Iterable[str] | None = None,
    ) -> ExcelFrame:
        columns = []
        if include_header:
            columns.append((header_name, self.columns))

        if column_names is None:
            column_names = []

        iterator = iter(column_names)
        for i in range(self.height):
            col_name: str
            try:
                col_name = next(iterator)
            except StopIteration:
                col_name = f"column_{i}"
            columns.append((col_name, self[i]))
        return ExcelFrame(dict(columns))

    def select(self, columns: list[str]) -> ExcelFrame:
        self._ordered_columns = columns
        # Update input by only taking the data specified in the column.
        self._input = {col: self._input[col] for col in self._ordered_columns}
        return self
