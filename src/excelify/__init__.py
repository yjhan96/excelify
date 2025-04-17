from abc import ABC, abstractmethod
from pathlib import Path
import polars as pl
from xlsxwriter import Workbook

from excelify._html import NotebookFormatter

RawInput = dict


def hello() -> str:
    return "Hello from excelify!"


def write_csv(path: Path) -> None:
    df = pl.DataFrame({"col1": [0, 1], "col2": [2, 3]})
    with Workbook(path) as wb:
        df.write_excel(workbook=wb, column_totals=True, autofit=True)


class Expr(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def eval(self):
        raise NotImplementedError

    @abstractmethod
    def to_formula(self):
        raise NotImplementedError

    @abstractmethod
    def to_html(self):
        raise NotImplementedError


class Constant(Expr):
    def __init__(self, value: int | float):
        super().__init__()
        self.value = value

    def eval(self):
        return self.value

    def to_formula(self):
        return self.value

    def __repr__(self) -> str:
        return f"Const({self.value})"

    def to_html(self):
        return str(self.value)


class ExcelFrame:
    def __init__(self, input: RawInput):
        self._input = {
            key: [Constant(value) for value in values] for key, values in input.items()
        }

    def __getitem__(self, idx_or_column: int | str):
        if isinstance(idx_or_column, int):
            # TODO: Come back to this.
            idx = idx_or_column
            return [series[idx] for series in self._input.values()]
        else:
            column = idx_or_column
            return self._input[column]

    @property
    def height(self) -> int:
        if self.width == 0:
            return 0
        return len(next(iter(self._input.values())))

    @property
    def width(self) -> int:
        return len(self._input)

    @property
    def shape(self) -> tuple[int, int]:
        return (self.height, self.width)

    @property
    def columns(self) -> list[str]:
        return list(self._input.keys())

    def _repr_html_(self):
        return "".join(NotebookFormatter(self).render())

    def write_excel(self, path: Path) -> None:
        with Workbook(path) as wb:
            worksheet = wb.add_worksheet()
            for i, (key, values) in enumerate(self._input.items()):
                worksheet.write(i, 0, key)
                for j, value in enumerate(values):
                    worksheet.write(i, j + 1, value.to_formula())
