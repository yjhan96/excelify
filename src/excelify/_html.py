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

import html
import re
from textwrap import dedent
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from types import TracebackType

    from excelify import ExcelFrame


def replace_consecutive_spaces(s: str) -> str:
    """Replace consecutive spaces with HTML non-breaking spaces."""
    return re.sub(r"( {2,})", lambda match: "&nbsp;" * len(match.group(0)), s)


class Tag:
    """Class for representing an HTML tag."""

    def __init__(
        self,
        elements: list[str],
        tag: str,
        attributes: dict[str, str] | None = None,
    ) -> None:
        self.tag = tag
        self.elements = elements
        self.attributes = attributes

    def __enter__(self) -> None:
        if self.attributes is not None:
            s = f"<{self.tag} "
            for k, v in self.attributes.items():
                s += f'{k}="{v}" '
            s = f"{s.rstrip()}>"
            self.elements.append(s)
        else:
            self.elements.append(f"<{self.tag}>")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.elements.append(f"</{self.tag}>")


class HTMLFormatter:
    def __init__(self, df: ExcelFrame, max_cols: int = 75, max_rows: int = 40):
        self.df = df
        self.elements: list[str] = []
        self.max_cols = max_cols
        self.max_rows = max_rows
        self.row_idx: Iterable[int | None]
        self.col_idx: Iterable[int | None]

        if max_rows < df.height:
            half, rest = divmod(max_rows, 2)
            self.row_idx = [
                *list(range(half + rest)),
                None,
                *list(range(df.height - half, df.height)),
            ]
        else:
            self.row_idx = range(df.height)

        if max_cols < df.width:
            self.col_idx = [
                *list(range(max_cols // 2)),
                None,
                *list(range(df.width - max_cols // 2, df.width)),
            ]
        else:
            self.col_idx = range(df.width)

    def write_header(self) -> None:
        with Tag(self.elements, "thead"):
            with Tag(self.elements, "tr"):
                columns = self.df.columns
                for c in self.col_idx:
                    with Tag(self.elements, "th"):
                        if c is None:
                            self.elements.append("&hellip;")
                        else:
                            self.elements.append(html.escape(columns[c]))

    def write_body(self) -> None:
        from excelify._excelframe import CellMapping

        mapping = CellMapping([(self.df, (0, 0))])

        with Tag(self.elements, "tbody"):
            for r in self.row_idx:
                with Tag(self.elements, "tr"):
                    for c in self.col_idx:
                        value: str
                        attrs: dict
                        if r is None or c is None:
                            value = "&hellip;"
                            attrs = {}
                        else:
                            col_name = self.df.columns[c]
                            cell = self.df[col_name][r]
                            value = str(cell.to_formula(mapping))
                            attrs = cell.attributes
                            try:
                                # TODO: Make the rounding configurable.
                                value = str(round(float(value), 2))
                            except ValueError:
                                pass
                            value = html.escape(value)
                        with Tag(self.elements, "td", attrs):
                            self.elements.append(value)

    def render(self) -> list[str]:
        width, height = self.df.shape
        shape = f"({width:_}, {height:_})"
        self.elements.append(f"<small>shape; {shape}</small>")

        with Tag(
            self.elements,
            "table",
            {"border": "1", "class": "dataframe"},
        ):
            self.write_header()
            self.write_body()
        return self.elements

    def write(self, inner: str) -> None:
        self.elements.append(inner)


class NotebookFormatter(HTMLFormatter):
    def write_style(self) -> None:
        style = """\
            <style>
            .dataframe > thead > tr,
            .dataframe > tbody > tr {
              text-align: right;
              white-space: pre-wrap;
            }
            </style>
        """
        self.write(dedent(style))

    def render(self) -> list[str]:
        with Tag(self.elements, "div"):
            self.write_style()
            super().render()

        return self.elements
