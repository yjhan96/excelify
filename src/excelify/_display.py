from __future__ import annotations

import csv
import json
import pickle
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Mapping, Sequence

import openpyxl
from lark import Lark

from excelify._cell import Cell
from excelify._cell_mapping import CellMapping, alpha_to_int, int_to_alpha
from excelify.formula._parser import create_parser

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


@dataclass
class TableConfig:
    start_row: int
    start_col: int
    width: int
    height: int

    @classmethod
    def of_json(cls, d_: dict):
        return cls(
            start_row=d_["start_row"],
            start_col=d_["start_col"],
            width=d_["width"],
            height=d_["height"],
        )


def to_excel(
    dfs: Sequence[tuple[ExcelFrame, tuple[int, int]]],
    path: Path,
    *,
    index_path: Path | None = None,
) -> None:
    path = Path(path) if isinstance(path, str) else path
    mapping = CellMapping(dfs)
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    assert worksheet is not None

    for df, (start_row, start_col) in dfs:
        for i, col in enumerate(df.columns):
            cells = df[col]
            worksheet.cell(row=start_row + 1, column=start_col + i + 1).value = col
            start_offset = 1

            for j, cell in enumerate(cells):
                formula = cell.to_formula(mapping)
                if not cell.cell_expr.is_primitive():
                    formula = f"={formula}"
                worksheet.cell(
                    row=start_row + j + start_offset + 1, column=start_col + i + 1
                ).value = formula

    workbook.save(path)

    if index_path is not None:
        index_json = [
            TableConfig(
                start_row=start_row,
                start_col=start_col,
                width=df.width,
                height=df.height,
            )
            for (df, (start_row, start_col)) in dfs
        ]
        with Path(index_path).open("w") as f:
            json.dump([asdict(config) for config in index_json], f, indent=4)


def _create_empty_dfs(
    workbook: openpyxl.Workbook, table_configs: Sequence[TableConfig]
) -> Sequence[ExcelFrame]:
    from excelify._excelframe import ExcelFrame

    worksheet = workbook.active
    assert worksheet is not None
    df_columns = [
        [
            worksheet[f"{int_to_alpha(col)}{config.start_row + 1}"].value
            for col in range(config.start_col, config.start_col + config.width)
        ]
        for config in table_configs
    ]
    return [
        ExcelFrame.empty(columns=columns, height=config.height)
        for columns, config in zip(df_columns, table_configs, strict=True)
    ]


def _get_cellpos_to_cellref_fn(
    table_configs: Sequence[TableConfig], dfs: Sequence[ExcelFrame]
) -> Callable[[str, int], Cell]:
    def cellpos_to_cellref(column_str: str, row_idx: int):
        abs_col_idx = alpha_to_int(column_str)
        abs_row_idx = row_idx - 1

        for df, config in zip(dfs, table_configs, strict=True):
            rel_col_idx = abs_col_idx - config.start_col
            rel_row_idx = abs_row_idx - config.start_row - 1

            if (
                rel_col_idx >= 0
                and rel_col_idx < df.width
                and rel_row_idx >= 0
                and rel_row_idx < df.height
            ):
                return df[df.columns[rel_col_idx]][rel_row_idx]
        raise ValueError(
            "The following cell position can't be mapped to one of the "
            f"loaded ExcelFrame's: {column_str}{row_idx}."
        )

    return cellpos_to_cellref


def _populate_df(
    workbook: openpyxl.Workbook, df: ExcelFrame, config: TableConfig, parser: Lark
) -> None:
    worksheet = workbook.active
    assert worksheet is not None
    for row_idx in range(config.height):
        for col_idx in range(config.width):
            df[df.columns[col_idx]][row_idx].cell_expr = parser.parse(
                str(
                    worksheet.cell(
                        row=config.start_row + 1 + 1 + row_idx,
                        column=config.start_col + 1 + col_idx,
                    ).value
                )
            )


def of_excel(*, path: Path | str, index_path: Path | str) -> Sequence[ExcelFrame]:
    path = Path(path) if isinstance(path, str) else path
    index_path = Path(index_path) if isinstance(index_path, str) else index_path
    with index_path.open("r") as f:
        index_json = json.load(f)
    table_configs = [TableConfig.of_json(d_) for d_ in index_json]
    workbook = openpyxl.load_workbook(path, read_only=True)
    dfs = _create_empty_dfs(workbook, table_configs)

    cellpos_to_cellref = _get_cellpos_to_cellref_fn(table_configs, dfs)
    parser = create_parser(cellpos_to_cellref)

    for df, config in zip(dfs, table_configs, strict=True):
        _populate_df(workbook, df, config, parser)
    return dfs


def of_csv(path: Path | str) -> ExcelFrame:
    from excelify._excelframe import ExcelFrame

    path = Path(path) if isinstance(path, str) else path
    with path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(
                f"Field names could not be inferred from the csv file {path}"
            )
        columns = reader.fieldnames
        d_ = {col: [] for col in columns}
        for row in reader:
            for col in columns:
                d_[col].append(row[col])
        return ExcelFrame(d_)


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
                    "value": value_cell.to_formula(
                        cell_mapping, style=evaluated_df.style
                    ),
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
