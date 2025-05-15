import pickle
from pathlib import Path
from typing import Sequence

import openpyxl

from excelify._excelframe import CellMapping, ExcelFrame

DATA_FILE = ".excelify-data/data.pickle"


def display(df: ExcelFrame):
    data_path = Path(DATA_FILE)
    data_path.parent.mkdir(exist_ok=True)

    with data_path.open("wb") as f:
        pickle.dump(df, f)


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
