# Copyright 2025 Albert Han
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Mapping

import numpy as np

from excelify._element import Element

if TYPE_CHECKING:
    from excelify._cell import Cell
    from excelify._excelframe import CellMapping
    from excelify._types import RawInput


# Operator precedence values (higher = higher precedence)
OPERATOR_PRECEDENCE = {
    "comparison": 1,  # =, <>, <, >, <=, >=
    "addition": 2,  # +, -
    "multiplication": 3,  # *, /
    "exponentiation": 4,  # ^
    "unary": 5,  # -x (negation)
    "default": 0,  # Constants, cell refs, functions
}


class InvalidCellException(Exception):
    pass


class CellExpr(ABC):
    @property
    @abstractmethod
    def dependencies(self) -> list[Cell]:
        raise NotImplementedError

    @abstractmethod
    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        raise NotImplementedError

    @abstractmethod
    def compute(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def is_primitive(self) -> bool:
        raise NotImplementedError

    def get_precedence(self) -> int:
        """Get operator precedence. Higher values = higher precedence."""
        return OPERATOR_PRECEDENCE["default"]

    def needs_parentheses(
        self, parent_precedence: int, is_right_operand: bool = False
    ) -> bool:
        """Check if this expression needs parentheses when used in a parent expression."""
        my_precedence = self.get_precedence()
        if my_precedence == 0:  # Non-operators never need parentheses
            return False
        if my_precedence < parent_precedence:
            return True
        # For same precedence, right operands of non-associative operators need parentheses
        if my_precedence == parent_precedence and is_right_operand:
            # Right-associative operators (like exponentiation) don't need parentheses on the right
            return parent_precedence != OPERATOR_PRECEDENCE["exponentiation"]
        return False

    def __truediv__(self, other: CellExpr) -> CellExpr:
        return Div(self, other)

    def __neg__(self) -> CellExpr:
        return Neg(self)

    def __add__(self, other: CellExpr) -> CellExpr:
        return Add(self, other)

    def __sub__(self, other: CellExpr) -> CellExpr:
        return Sub(self, other)

    def __mul__(self, other: CellExpr) -> CellExpr:
        return Mult(self, other)

    def __pow__(self, other: CellExpr) -> CellExpr:
        return Pow(self, other)

    @abstractmethod
    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        raise NotImplementedError


class Empty(CellExpr):
    def __init__(self):
        super().__init__()

    @property
    def dependencies(self) -> list[Cell]:
        return []

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        return ""

    def compute(self) -> Any:
        return None

    def is_primitive(self) -> bool:
        return True

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        return self


class Invalid(CellExpr):
    def __init__(self):
        super().__init__()

    @property
    def dependencies(self) -> list[Cell]:
        return []

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        raise InvalidCellException("Invalid cell!")

    def compute(self) -> Any:
        return None

    def is_primitive(self) -> bool:
        return True

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        return self


class Constant(CellExpr):
    def __init__(self, value: int | float | str):
        super().__init__()
        self.value = value

    @property
    def dependencies(self) -> list[Cell]:
        return []

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        return self.value

    def compute(self) -> Any:
        return self.value

    def is_primitive(self) -> bool:
        return True

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        return self


def _get_cell_mapping(
    element: Element, mapping: CellMapping, raise_if_missing: bool
) -> str:
    if raise_if_missing or element in mapping:
        return mapping[element]
    else:
        _, col_name, idx = element
        return f"???:{col_name}:{idx}"


class CellRef(CellExpr):
    def __init__(self, cell_ref: Cell):
        super().__init__()
        self._cell_ref = cell_ref

    @property
    def dependencies(self) -> list[Cell]:
        return [self._cell_ref]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        return _get_cell_mapping(self._cell_ref.element, mapping, raise_if_missing)

    def compute(self) -> Any:
        return self._cell_ref.last_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        if self._cell_ref.element in ref_map:
            return CellRef(ref_map[self._cell_ref.element])
        else:
            return self


class SumCellsRef(CellExpr):
    def __init__(self, cells: list[Cell]):
        super().__init__()
        self._cells = cells

    @property
    def dependencies(self) -> list[Cell]:
        return [cell for cell in self._cells]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        from_cell = _get_cell_mapping(self._cells[0].element, mapping, raise_if_missing)
        to_cell = _get_cell_mapping(self._cells[-1].element, mapping, raise_if_missing)
        return f"SUM({from_cell}:{to_cell})"

    def compute(self) -> Any:
        values = [cell.last_value for cell in self._cells]

        if any(value is None for value in values):
            return None
        else:
            return sum(values)

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        if any(self._cells[i].element in ref_map for i in range(len(self._cells))):
            cells = []
            for i in range(len(self._cells)):
                if self._cells[i].element in ref_map:
                    cells.append(ref_map[self._cells[i].element])
                else:
                    cells.append(self._cells[i])
            return SumCellsRef(cells)
        else:
            return self


class AverageCellsRef(CellExpr):
    def __init__(self, cells: list[Cell]):
        super().__init__()
        self._cells = cells

    @property
    def dependencies(self) -> list[Cell]:
        return [cell for cell in self._cells]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        from_cell = _get_cell_mapping(self._cells[0].element, mapping, raise_if_missing)
        to_cell = _get_cell_mapping(self._cells[-1].element, mapping, raise_if_missing)
        return f"AVERAGE({from_cell}:{to_cell})"

    def compute(self) -> Any:
        values = [cell.last_value for cell in self._cells]

        if any(value is None for value in values):
            return None
        else:
            return sum(values) / len(values)

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        if any(self._cells[i].element in ref_map for i in range(len(self._cells))):
            cells = []
            for i in range(len(self._cells)):
                if self._cells[i].element in ref_map:
                    cells.append(ref_map[self._cells[i].element])
                else:
                    cells.append(self._cells[i])
            return AverageCellsRef(cells)
        else:
            return self


class SumProdCellsRef(CellExpr):
    def __init__(self, columns: list[list[Cell]]):
        super().__init__()
        self._columns = columns

    @property
    def dependencies(self) -> list[Cell]:
        return [cell for column in self._columns for cell in column]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        cell_ranges = [
            (
                _get_cell_mapping(col[0].element, mapping, raise_if_missing),
                _get_cell_mapping(col[-1].element, mapping, raise_if_missing),
            )
            for col in self._columns
        ]
        cell_ranges_str = ",".join(
            [f"{from_cell}:{to_cell}" for (from_cell, to_cell) in cell_ranges]
        )
        return f"SUMPRODUCT({cell_ranges_str})"

    def compute(self) -> Any:
        values = [[cell.last_value for cell in column] for column in self._columns]
        if any(value is None for column in values for value in column):
            return None
        else:
            return sum(
                [
                    math.prod([column[i] for column in values])
                    for i in range(len(values[0]))
                ]
            )

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        if any(cell.element in ref_map for column in self._columns for cell in column):
            columns = [
                [
                    ref_map[cell.element] if cell.element in ref_map else cell
                    for cell in column
                ]
                for column in self._columns
            ]
            return SumProdCellsRef(columns)
        else:
            return self


class Mult(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def get_precedence(self) -> int:
        return OPERATOR_PRECEDENCE["multiplication"]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )

            # Add parentheses only if needed
            if self._left_cell_expr.needs_parentheses(self.get_precedence(), False):
                left_cell_formula = f"({left_cell_formula})"
            if self._right_cell_expr.needs_parentheses(self.get_precedence(), True):
                right_cell_formula = f"({right_cell_formula})"

            return f"{left_cell_formula} * {right_cell_formula}"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            return left_value * right_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Mult(left_cell_expr, right_cell_expr)


class Add(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def get_precedence(self) -> int:
        return OPERATOR_PRECEDENCE["addition"]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )

            # Add parentheses only if needed
            if self._left_cell_expr.needs_parentheses(self.get_precedence(), False):
                left_cell_formula = f"({left_cell_formula})"
            if self._right_cell_expr.needs_parentheses(self.get_precedence(), True):
                right_cell_formula = f"({right_cell_formula})"

            return f"{left_cell_formula} + {right_cell_formula}"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()
        if left_value is None or right_value is None:
            return None
        else:
            return left_value + right_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Add(left_cell_expr, right_cell_expr)


class Div(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def get_precedence(self) -> int:
        return OPERATOR_PRECEDENCE["multiplication"]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )

            # Add parentheses only if needed
            if self._left_cell_expr.needs_parentheses(self.get_precedence(), False):
                left_cell_formula = f"({left_cell_formula})"
            if self._right_cell_expr.needs_parentheses(self.get_precedence(), True):
                right_cell_formula = f"({right_cell_formula})"

            return f"{left_cell_formula} / {right_cell_formula}"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            try:
                return left_value / right_value
            except ZeroDivisionError:
                return np.inf

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Div(left_cell_expr, right_cell_expr)


class Sub(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def get_precedence(self) -> int:
        return OPERATOR_PRECEDENCE["addition"]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )

            # Add parentheses only if needed
            if self._left_cell_expr.needs_parentheses(self.get_precedence(), False):
                left_cell_formula = f"({left_cell_formula})"
            if self._right_cell_expr.needs_parentheses(self.get_precedence(), True):
                right_cell_formula = f"({right_cell_formula})"

            return f"{left_cell_formula} - {right_cell_formula}"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            return left_value - right_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Sub(left_cell_expr, right_cell_expr)


class Max(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            return f"MAX({left_cell_formula}, {right_cell_formula})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            return max(left_value, right_value)

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Max(left_cell_expr, right_cell_expr)


class Min(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            return f"MIN({left_cell_formula}, {right_cell_formula})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            return min(left_value, right_value)

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Min(left_cell_expr, right_cell_expr)


class If(CellExpr):
    def __init__(
        self, condition_expr: CellExpr, true_expr: CellExpr, false_expr: CellExpr
    ):
        super().__init__()
        self._condition_expr = condition_expr
        self._true_expr = true_expr
        self._false_expr = false_expr

    @property
    def dependencies(self) -> list[Cell]:
        return (
            self._condition_expr.dependencies
            + self._true_expr.dependencies
            + self._false_expr.dependencies
        )

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            condition_formula = self._condition_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            true_formula = self._true_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            false_formula = self._false_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            return f"IF({condition_formula}, {true_formula}, {false_formula})"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        condition_value = self._condition_expr.compute()

        if condition_value is None:
            return None

        # Evaluate condition as boolean
        if condition_value:
            return self._true_expr.compute()
        else:
            return self._false_expr.compute()

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        condition_expr = self._condition_expr.update_cell_refs(ref_map)
        true_expr = self._true_expr.update_cell_refs(ref_map)
        false_expr = self._false_expr.update_cell_refs(ref_map)

        if (
            condition_expr == self._condition_expr
            and true_expr == self._true_expr
            and false_expr == self._false_expr
        ):
            return self
        else:
            return If(condition_expr, true_expr, false_expr)


class Compare(CellExpr):
    def __init__(
        self, left_cell_expr: CellExpr, right_cell_expr: CellExpr, operator: str
    ):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr
        self._operator = operator  # ">", "<", ">=", "<=", "=", "<>"

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def get_precedence(self) -> int:
        return OPERATOR_PRECEDENCE["comparison"]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )

            # Add parentheses only if needed
            if self._left_cell_expr.needs_parentheses(self.get_precedence(), False):
                left_cell_formula = f"({left_cell_formula})"
            if self._right_cell_expr.needs_parentheses(self.get_precedence(), True):
                right_cell_formula = f"({right_cell_formula})"

            return f"{left_cell_formula} {self._operator} {right_cell_formula}"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None

        if self._operator == ">":
            return left_value > right_value
        elif self._operator == "<":
            return left_value < right_value
        elif self._operator == ">=":
            return left_value >= right_value
        elif self._operator == "<=":
            return left_value <= right_value
        elif self._operator == "=":
            return left_value == right_value
        elif self._operator == "<>":
            return left_value != right_value
        else:
            return None

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Compare(left_cell_expr, right_cell_expr, self._operator)


class Pow(CellExpr):
    def __init__(self, left_cell_expr: CellExpr, right_cell_expr: CellExpr):
        super().__init__()
        self._left_cell_expr = left_cell_expr
        self._right_cell_expr = right_cell_expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._left_cell_expr.dependencies + self._right_cell_expr.dependencies

    def get_precedence(self) -> int:
        return OPERATOR_PRECEDENCE["exponentiation"]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            left_cell_formula = self._left_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )
            right_cell_formula = self._right_cell_expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )

            # Add parentheses only if needed
            if self._left_cell_expr.needs_parentheses(self.get_precedence(), False):
                left_cell_formula = f"({left_cell_formula})"
            if self._right_cell_expr.needs_parentheses(self.get_precedence(), True):
                right_cell_formula = f"({right_cell_formula})"

            return f"{left_cell_formula} ^ {right_cell_formula}"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> Any:
        left_value = self._left_cell_expr.compute()
        right_value = self._right_cell_expr.compute()

        if left_value is None or right_value is None:
            return None
        else:
            return left_value**right_value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        left_cell_expr = self._left_cell_expr.update_cell_refs(ref_map)
        right_cell_expr = self._right_cell_expr.update_cell_refs(ref_map)

        if (
            left_cell_expr == self._left_cell_expr
            and right_cell_expr == self._right_cell_expr
        ):
            return self
        else:
            return Pow(left_cell_expr, right_cell_expr)


class Neg(CellExpr):
    def __init__(self, expr: CellExpr):
        super().__init__()
        self._expr = expr

    @property
    def dependencies(self) -> list[Cell]:
        return self._expr.dependencies

    def get_precedence(self) -> int:
        return OPERATOR_PRECEDENCE["unary"]

    def to_formula(self, mapping: CellMapping, *, raise_if_missing: bool) -> RawInput:
        try:
            expr_formula = self._expr.to_formula(
                mapping, raise_if_missing=raise_if_missing
            )

            # Add parentheses only if needed
            if self._expr.needs_parentheses(self.get_precedence(), False):
                expr_formula = f"({expr_formula})"

            return f"-{expr_formula}"
        except InvalidCellException:
            return "ERROR"

    def compute(self) -> None:
        value = self._expr.compute()
        if value is None:
            return None
        else:
            return -value

    def is_primitive(self) -> bool:
        return False

    def update_cell_refs(self, ref_map: Mapping[Element, Cell]) -> CellExpr:
        expr = self._expr.update_cell_refs(ref_map)
        if expr == self._expr:
            return self
        else:
            return Neg(expr)
