from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from excelify._col_conversion import int_to_alpha
from excelify._element import Element
from excelify._styler import DisplayAxis

if TYPE_CHECKING:
    from excelify._excelframe import ExcelFrame


class CellMapping:
    def __init__(
        self,
        dfs: Sequence[tuple[ExcelFrame, tuple[int, int]]],
        header_in_table: bool = True,
    ):
        self._id_to_df = {df.id: df for df, _ in dfs}
        self._id_to_start_pos = {df.id: start_pos for df, start_pos in dfs}
        self._columns = {
            df.id: {c: i for i, c in enumerate(df.columns)} for df, _ in dfs
        }
        self._header_in_table = header_in_table

    def get_cell_index(self, element: Element) -> tuple[int, int]:
        id, col_name, idx = element
        start_row, start_col = self._id_to_start_pos[id]
        match self._id_to_df[id].style.display_axis:
            case DisplayAxis.VERTICAL:
                return (start_row + idx + 1, start_col + self._columns[id][col_name])
            case DisplayAxis.HORIZONTAL:
                return (start_row + self._columns[id][col_name], start_col + idx + 1)
            case other:
                raise ValueError(f"Unknown display axis: {other}")

    def __getitem__(self, element: Element) -> str:
        id, col_name, idx = element
        start_row, start_col = self._id_to_start_pos[id]
        match self._id_to_df[id].style.display_axis:
            case DisplayAxis.VERTICAL:
                col_alpha_idx = int_to_alpha(self._columns[id][col_name] + start_col)
                row_idx = start_row + idx + 1 + (1 if self._header_in_table else 0)
                return f"{col_alpha_idx}{row_idx}"
            case DisplayAxis.HORIZONTAL:
                col_alpha_idx = int_to_alpha(
                    start_col + (1 if self._header_in_table else 0) + idx
                )
                row_idx = start_row + 1 + self._columns[id][col_name]
                return f"{col_alpha_idx}{row_idx}"
            case other:
                raise ValueError(f"Unknown display axis: {other}")

    def __contains__(self, element: Element) -> bool:
        id, col_name, _ = element
        if id not in self._columns:
            return False
        if col_name not in self._columns[id]:
            return False
        return True
