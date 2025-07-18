from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, NamedTuple, Sequence, overload

from typing_extensions import Self

import openpyxl
import openpyxl.cell
import openpyxl.styles
import openpyxl.styles.numbers

from excelify._cell import Cell
from excelify._col_conversion import alpha_to_int
from excelify._types import RawInput


@dataclass(frozen=True)
class NumberFormatter:
    decimals: int


@dataclass(frozen=True)
class IntegerFormatter:
    pass


@dataclass(frozen=True)
class CurrencyFormatter:
    accounting: bool


@dataclass(frozen=True)
class PercentFormatter:
    pass


@dataclass(frozen=True)
class ValueColorFormatter:
    color: str


Formatter = (
    NumberFormatter
    | IntegerFormatter
    | CurrencyFormatter
    | PercentFormatter
    | ValueColorFormatter
)


@dataclass
class FormattedValue:
    value: RawInput
    color: str = "black"


def _apply_format(formatter: Formatter, formatted_value: FormattedValue):
    value = formatted_value.value
    if value is None:
        return ""
    match formatter:
        case NumberFormatter(decimals):
            formatted_value.value = f"{float(value):,.{decimals}f}"
        case IntegerFormatter():
            formatted_value.value = f"{int(float(value)):,}"
        case CurrencyFormatter(accounting):
            float_value = float(value)
            if accounting and float_value < 0:
                formatted_value.value = f"({abs(float_value):,.2f})"
                formatted_value.color = "red"
            else:
                formatted_value.value = f"${float_value:,.2f}"
        case PercentFormatter():
            formatted_value.value = f"{float(value) * 100:,.2f}%"
        case ValueColorFormatter(color):
            formatted_value.color = color
        case _:
            raise ValueError("Impossible")


def _color_to_hex(color: str) -> str:
    """
    Converts known color name into a hex value so openpyxl can understand.
    """
    color_map = {
        "black": "000000",
        "white": "FFFFFF",
        "red": "FF0000",
        "green": "008000",
        "blue": "0000FF",
        "yellow": "FFFF00",
        "cyan": "00FFFF",
        "magenta": "FF00FF",
        "orange": "FFA500",
        "purple": "800080",
        "pink": "FFC0CB",
        "brown": "A52A2A",
        "gray": "808080",
        "grey": "808080",
        "lime": "00FF00",
        "navy": "000080",
        "teal": "008080",
        "olive": "808000",
        "maroon": "800000",
        "silver": "C0C0C0",
        "gold": "FFD700",
        "violet": "EE82EE",
        "indigo": "4B0082",
        "coral": "FF7F50",
        "salmon": "FA8072",
        "khaki": "F0E68C",
        "crimson": "DC143C",
        "chocolate": "D2691E",
        "darkblue": "00008B",
        "darkgreen": "006400",
        "darkred": "8B0000",
        "lightblue": "ADD8E6",
        "lightgreen": "90EE90",
        "lightgray": "D3D3D3",
        "lightgrey": "D3D3D3",
        "darkgray": "A9A9A9",
        "darkgrey": "A9A9A9",
    }

    normalized_color = color.lower().strip()
    if normalized_color in color_map:
        return color_map[normalized_color]
    else:
        # If color is already a hex code (with or without #), return it
        if normalized_color.startswith("#"):
            return normalized_color[1:]
        elif len(normalized_color) == 6 and all(
            c in "0123456789abcdef" for c in normalized_color
        ):
            return normalized_color.upper()
        else:
            # Default to black if color is not recognized
            return "000000"


def _apply_format_excel(formatter: Formatter, sheet_cell: openpyxl.cell.Cell):
    match formatter:
        case NumberFormatter(decimals):
            sheet_cell.number_format = (
                openpyxl.styles.numbers.FORMAT_NUMBER_COMMA_SEPARATED1
            )
        case IntegerFormatter():
            sheet_cell.number_format = openpyxl.styles.numbers.FORMAT_NUMBER
        case CurrencyFormatter(accounting):
            if accounting:
                sheet_cell.number_format = '"$"#,##0.00_);[Red](#,##0.00)'
            else:
                sheet_cell.number_format = (
                    openpyxl.styles.numbers.FORMAT_CURRENCY_USD_SIMPLE
                )
        case PercentFormatter():
            sheet_cell.number_format = openpyxl.styles.numbers.FORMAT_PERCENTAGE
        case ValueColorFormatter(color):
            sheet_cell.font = openpyxl.styles.Font(color=_color_to_hex(color))
        case _:
            pass


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


@dataclass
class ColumnStyle:
    col_width: int | None = None


def _default_column_style():
    return ColumnStyle()


class DisplayAxis(Enum):
    VERTICAL = 0
    HORIZONTAL = 1


class TableStyler:
    def __init__(self) -> None:
        self.conditions: list[Apply] = []
        self._display_axis: DisplayAxis = DisplayAxis.VERTICAL
        self._column_groups: list[tuple[str, list[str]]] = []
        self._column_renames: dict[str, str] = {}

    @property
    def display_axis(self) -> DisplayAxis:
        return self._display_axis

    @property
    def column_groups(self) -> list[tuple[str, list[str]]]:
        return self._column_groups

    @property
    def column_renames(self) -> dict[str, str]:
        return self._column_renames

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
        self,
        columns: Sequence[str] | None = None,
        rows: Sequence[int] | None = None,
        accounting: bool = False,
    ) -> Self:
        self.conditions.append(
            Apply(CurrencyFormatter(accounting), Predicate(columns=columns, rows=rows))
        )
        return self

    def fmt_percent(
        self, columns: Sequence[str] | None = None, rows: Sequence[int] | None = None
    ) -> Self:
        self.conditions.append(
            Apply(PercentFormatter(), Predicate(columns=columns, rows=rows))
        )
        return self

    def display_horizontally(self) -> Self:
        self._display_axis = DisplayAxis.HORIZONTAL
        return self

    def display_vertically(self) -> Self:
        self._display_axis = DisplayAxis.VERTICAL
        return self

    def group_columns(self, column_groups: list[tuple[str, list[str]]]) -> Self:
        columns = Counter([col for _, columns in column_groups for col in columns])
        duplicate_columns = {col for col, counter in columns.items() if counter > 1}
        if duplicate_columns:
            raise ValueError(
                f"A column can't be specified in multiple column groups: {list(duplicate_columns)}"
            )
        self._column_groups = column_groups
        return self

    def rename_columns(self, column_renames: dict[str, str]) -> Self:
        for original_name, new_name in column_renames.items():
            self._column_renames[original_name] = new_name
        return self

    def value_color(
        self,
        columns: Sequence[str] | None = None,
        rows: Sequence[int] | None = None,
        color: str = "blue",
    ):
        self.conditions.append(
            Apply(ValueColorFormatter(color), Predicate(columns=columns, rows=rows))
        )

    def format_value(self, cell: Cell, value: RawInput) -> FormattedValue:
        formatted_value = FormattedValue(value)
        for formatter, predicate in self.conditions:
            if predicate(cell):
                try:
                    _apply_format(formatter, formatted_value)
                except TypeError:
                    formatted_value.value = "ERROR"
                    break
        return formatted_value

    def format_value_excel(self, cell: Cell, sheet_cell: openpyxl.cell.Cell):
        for formatter, predicate in self.conditions:
            if predicate(cell):
                _apply_format_excel(formatter, sheet_cell)


class SheetStyler:
    def __init__(self) -> None:
        self._column_style: dict[int, ColumnStyle] = defaultdict(_default_column_style)

    def _validate_columns(self, columns: Iterable[str | int]):
        for col_name in columns:
            if not (
                (
                    isinstance(col_name, str)
                    and col_name.isalpha()
                    and col_name.isupper()
                )
                or (isinstance(col_name, int) and col_name >= 0)
            ):
                raise ValueError(f"Following column name is invalid: {col_name}")

    def cols_width(
        self,
        cases: dict[str, int] | dict[int, int] | dict[str | int, int] | None = None,
    ) -> Self:
        if cases is not None:
            self._validate_columns(cases.keys())
            for col_name, width_value in cases.items():
                key = alpha_to_int(col_name) if isinstance(col_name, str) else col_name
                self._column_style[key].col_width = width_value
        return self

    def to_json(self) -> dict[str, int]:
        col_style = {
            str(col_idx): cell_width.col_width
            for col_idx, cell_width in self._column_style.items()
            if cell_width.col_width is not None
        }
        return col_style
