from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from excelify._element import Element

if TYPE_CHECKING:
    from excelify._excelframe import ExcelFrame


class CellMapping:
    def __init__(self, dfs: Sequence[tuple[ExcelFrame, tuple[int, int]]]):
        self._id_to_start_pos = {df.id: start_pos for df, start_pos in dfs}
        self._columns = {
            df.id: {c: i for i, c in enumerate(df.columns)} for df, _ in dfs
        }

    def _int_to_alpha(self, idx: int) -> str:
        num_alphabets = 26

        if idx == 0:
            return "A"
        result = []
        while idx > 0:
            rem = idx % num_alphabets
            if len(result) == 0:
                result.append(chr(ord("A") + rem))
            else:
                result.append(chr(ord("A") + rem - 1))
            idx = idx // num_alphabets
        return "".join(reversed(result))

    def __getitem__(self, element: Element) -> str:
        id, col_name, idx = element
        start_row, start_col = self._id_to_start_pos[id]
        col_idx = self._int_to_alpha(self._columns[id][col_name] + start_col)
        row_idx = idx + start_row + 1
        return f"{col_idx}{row_idx}"
