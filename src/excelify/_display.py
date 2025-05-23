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


def display(dfs: Sequence[tuple[ExcelFrame, tuple[int, int]]]):
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


def _df_to_json(
    df: ExcelFrame,
    *,
    cell_mapping: CellMapping,
    dfs_start_positions: Mapping[uuid.UUID, tuple[int, int]],
    dfs_col_to_offset: Mapping[uuid.UUID, Mapping[str, int]],
    include_header: bool,
) -> list[list[dict]]:
    sheet = []
    evaluated_df = df.evaluate()
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
                    "value": value_cell.to_formula(cell_mapping),
                    "depIndices": dep_indices,
                    "is_editable": formula_cell.is_editable,
                }
            )
        sheet.append(curr_column)
    return sheet


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
    return sheets
