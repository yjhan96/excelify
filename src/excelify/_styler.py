from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple, Self, Sequence

from excelify._cell import Cell
from excelify._types import RawInput


@dataclass(frozen=True)
class NumberFormatter:
    decimals: int


@dataclass(frozen=True)
class IntegerFormatter:
    pass


@dataclass(frozen=True)
class CurrencyFormatter:
    pass


@dataclass(frozen=True)
class PercentFormatter:
    pass


Formatter = NumberFormatter | IntegerFormatter | CurrencyFormatter | PercentFormatter


def _format(formatter: Formatter, value: RawInput) -> str:
    match formatter:
        case NumberFormatter(decimals):
            return f"{float(value):,.{decimals}f}"
        case IntegerFormatter():
            return f"{int(float(value)):,}"
        case CurrencyFormatter():
            return f"${float(value):,.2f}"
        case PercentFormatter():
            return f"{float(value) * 100:,.0f}%"
        case _:
            raise ValueError("Impossible")


class Predicate:
    def __init__(self, *, columns: Sequence[str] | None, rows: Sequence[int] | None):
        self._columns = columns
        self._rows = rows

        if all(e is None for e in [self._columns, self._rows]):
            raise ValueError("None of the conditions is defined.")

    def __call__(self, cell: Cell) -> bool:
        if self._columns is not None and cell.element.col_name not in self._columns:
            return False
        if self._rows is not None and cell.element.idx not in self._rows:
            return False
        return True


class Apply(NamedTuple):
    formatter: Formatter
    predicate: Predicate


DEFAULT_CELL_WIDTH = 80


@dataclass
class ColumnStyle:
    col_width: int | None = None


def _default_column_style():
    return ColumnStyle()


class Styler:
    def __init__(self) -> None:
        self.conditions: list[Apply] = []
        self._column_style: dict[str, ColumnStyle] = defaultdict(_default_column_style)

    def fmt_number(
        self,
        columns: Sequence[str] | None = None,
        rows: Sequence[int] | None = None,
        decimals: int = 2,
    ) -> Self:
        self.conditions.append(
            Apply(NumberFormatter(decimals), Predicate(columns=columns, rows=rows))
        )
        return self

    def fmt_integer(
        self, columns: Sequence[str] | None = None, rows: Sequence[int] | None = None
    ) -> Self:
        self.conditions.append(
            Apply(IntegerFormatter(), Predicate(columns=columns, rows=rows))
        )
        return self

    def fmt_currency(
        self, columns: Sequence[str] | None = None, rows: Sequence[int] | None = None
    ) -> Self:
        self.conditions.append(
            Apply(CurrencyFormatter(), Predicate(columns=columns, rows=rows))
        )
        return self

    def fmt_percent(
        self, columns: Sequence[str] | None = None, rows: Sequence[int] | None = None
    ) -> Self:
        self.conditions.append(
            Apply(PercentFormatter(), Predicate(columns=columns, rows=rows))
        )
        return self

    def cols_width(self, cases: dict[str, int] | None = None) -> Self:
        if cases is not None:
            for col_name, width_value in cases.items():
                self._column_style[col_name].col_width = width_value
        return self

    def apply_value(self, cell: Cell, value: RawInput) -> RawInput:
        for formatter, predicate in self.conditions:
            if predicate(cell):
                value = _format(formatter, value)
        return value

    @property
    def column_style(self) -> dict[str, ColumnStyle]:
        return self._column_style
