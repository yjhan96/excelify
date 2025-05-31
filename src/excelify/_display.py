from __future__ import annotations

import pickle
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Mapping, Sequence

import openpyxl

from excelify._cell_mapping import CellMapping

if TYPE_CHECKING:
    from excelify._excelframe import ExcelFrame


DATA_FILE = ".excelify-data/data.pickle"
DFS_TO_DISPLAY: Sequence[tuple[ExcelFrame, tuple[int, int]]] | None = None


def display(dfs: Sequence[tuple[ExcelFrame, tuple[int, int]]], to_disk: bool = False):
    global DFS_TO_DISPLAY
    DFS_TO_DISPLAY = dfs

    if to_disk:
        data_path = Path(DATA_FILE)
        data_path.parent.mkdir(exist_ok=True)

        with data_path.open("wb") as f:
            pickle.dump(dfs, f)


def to_excel(dfs: Sequence[tuple[ExcelFrame, tuple[int, int]]], path: Path) -> None:
    path = Path(path) if isinstance(path, str) else path
    mapping = CellMapping(dfs)
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    assert worksheet is not None

    for df, (start_row, start_col) in dfs:
        start_row, start_col = start_row + 1, start_col + 1
        for i, col in enumerate(df.columns):
            cells = df[col]
            worksheet.cell(row=start_row, column=start_col + i).value = col
            start_offset = 1

            for j, cell in enumerate(cells):
                formula = cell.to_formula(mapping)
                if not cell.cell_expr.is_primitive():
                    formula = f"={formula}"
                worksheet.cell(
                    row=start_row + j + start_offset, column=start_col + i
                ).value = formula

    workbook.save(path)


def _get_dfs_col_to_offset(
    dfs: Sequence[tuple[ExcelFrame, tuple[int, int]]],
) -> Mapping[uuid.UUID, Mapping[str, int]]:
    return {df.id: {col: i for i, col in enumerate(df.columns)} for df, _ in dfs}


def _get_df_col_style_json(
    df: ExcelFrame, *, start_position: tuple[int, int]
) -> dict[int, str]:
    col_style = {}
    _, start_col = start_position
    for idx, col_name in enumerate(df.columns):
        col_style[start_col + idx] = df.style.column_style[col_name].col_width
    return col_style


def _get_dfs_col_style_json(
    dfs: Sequence[ExcelFrame],
    *,
    dfs_start_positions: Mapping[uuid.UUID, tuple[int, int]],
):
    combined_col_style = {}
    for df in dfs:
        col_style = _get_df_col_style_json(
            df, start_position=dfs_start_positions[df.id]
        )
        for col_idx, cell_width in col_style.items():
            if col_idx in combined_col_style:
                if combined_col_style[col_idx] != cell_width:
                    raise ValueError(
                        f"Inconsistent cell width for column index {col_idx}: "
                        f"{cell_width} vs. {combined_col_style[col_idx]}"
                    )
            else:
                combined_col_style[col_idx] = cell_width
    return combined_col_style


def _df_to_json(
    df: ExcelFrame,
    *,
    cell_mapping: CellMapping,
    dfs_start_positions: Mapping[uuid.UUID, tuple[int, int]],
    dfs_col_to_offset: Mapping[uuid.UUID, Mapping[str, int]],
    include_header: bool,
) -> list[list[dict]]:
    table = []
    evaluated_df = df.evaluate(inherit_style=True)
    for col_name in df.columns:
        formula_column = df[col_name]
        value_column = evaluated_df[col_name]
        curr_column: list
        if include_header:
            curr_column = [
                {
                    "formula": col_name,
                    "value": col_name,
                    "depIndices": [],
                    "is_editable": False,
                }
            ]
        else:
            curr_column = []

        for formula_cell, value_cell in zip(formula_column, value_column, strict=True):
            deps = formula_cell.dependencies
            dep_indices = []
            for dep in deps:
                dep_id, dep_col_name, dep_idx = dep.element
                dep_start_row, dep_start_col = dfs_start_positions[dep_id]
                dep_indices.append(
                    (
                        dep_start_row + dep_idx,
                        dep_start_col + dfs_col_to_offset[dep_id][dep_col_name],
                    )
                )
            curr_column.append(
                {
                    "formula": formula_cell.to_formula(cell_mapping),
                    "value": value_cell.to_formula(cell_mapping, evaluated_df.style),
                    "depIndices": dep_indices,
                    "is_editable": formula_cell.is_editable,
                    "cellWidth": df.style.column_style[
                        formula_cell.element.col_name
                    ].col_width,
                }
            )
        table.append(curr_column)
    return table


def to_json(
    dfs: Sequence[tuple[ExcelFrame, tuple[int, int]]], include_header: bool = True
):
    sheets = []
    if include_header:
        dfs = [(df, (start_row + 1, start_col)) for (df, (start_row, start_col)) in dfs]
    cell_mapping = CellMapping(dfs)
    dfs_start_positions = {df.id: start_pos for df, start_pos in dfs}
    dfs_col_to_offset = _get_dfs_col_to_offset(dfs)
    sheets = [
        _df_to_json(
            df,
            cell_mapping=cell_mapping,
            dfs_start_positions=dfs_start_positions,
            dfs_col_to_offset=dfs_col_to_offset,
            include_header=include_header,
        )
        for df, _ in dfs
    ]
    col_styles = _get_dfs_col_style_json(
        [df for df, _ in dfs],
        dfs_start_positions=dfs_start_positions,
    )
    return {"tables": sheets, "colStyles": col_styles}
