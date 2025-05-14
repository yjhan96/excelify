import pickle
from pathlib import Path

from excelify._excelframe import ExcelFrame

DATA_FILE = ".excelify-data/data.pickle"


def display(df: ExcelFrame):
    data_path = Path(DATA_FILE)
    data_path.parent.mkdir(exist_ok=True)

    with data_path.open("wb") as f:
        pickle.dump(df, f)
