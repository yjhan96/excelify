from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import NamedTuple, Self, Sequence

from excelify._cell import Cell


class Formatter(Enum):
    INTEGER = 1
    CURRENCY = 2
    PERCENT = 3


def _format(formatter: Formatter, value: str) -> str:
    match formatter:
        case Formatter.INTEGER:
            return f"{int(float(value)):,}"
        case Formatter.CURRENCY:
            return f"${value}"
        case Formatter.PERCENT:
            return f"{float(value) * 100:.2f}%"
        case _:
            raise ValueError("Impossible")


class Predicate(ABC):
    @abstractmethod
    def __call__(self, cell: Cell) -> bool:
        raise NotImplementedError


class MatchesColumn(Predicate):
    def __init__(self, col_names: Sequence[str]):
        self._col_names = set(col_names)

    def __call__(self, cell: Cell) -> bool:
        return cell.element.col_name in self._col_names


class Apply(NamedTuple):
    formatter: Formatter
    predicate: Predicate


class Styler:
    def __init__(self) -> None:
        self.conditions: list[Apply] = []

    def fmt_integer(self, columns: Sequence[str] | None = None) -> Self:
        if columns is not None:
            self.conditions.append(Apply(Formatter.INTEGER, MatchesColumn(columns)))
        return self

    def fmt_currency(self, columns: Sequence[str] | None = None) -> Self:
        if columns is not None:
            self.conditions.append(Apply(Formatter.CURRENCY, MatchesColumn(columns)))
        return self

    def fmt_percent(self, columns: Sequence[str] | None = None) -> Self:
        if columns is not None:
            self.conditions.append(Apply(Formatter.PERCENT, MatchesColumn(columns)))
        return self

    def apply_value(self, cell: Cell, value: str) -> str:
        for formatter, predicate in self.conditions:
            if predicate(cell):
                value = _format(formatter, value)
        return value
