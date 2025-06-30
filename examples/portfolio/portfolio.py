import os
from pathlib import Path

import excelify as el

df = el.of_csv(Path(os.path.abspath(__file__)).parent / "example.csv")

columns = [
    "symbol",
    "type",
    "unit",
    "unit_to_add",
    "price",
    "total_price",
    "fraction",
    "ideal_fraction",
    "delta",
    "delta_in_units",
]

df = df.with_columns(
    unit_to_add=el.lit([0 for _ in range(df.height)]),
    total_price=(el.col("unit") + el.col("unit_to_add")) * el.col("price"),
)

total_df = el.ExcelFrame.empty(
    columns=["total", "cash", "cash_after_purchase"], height=1
)
total_df = total_df.with_columns(
    total=el.sumprod(["unit", "price"], from_=df) + el.col("cash"),
    cash=el.lit([5_000]),
    cash_after_purchase=el.col("cash") - el.sumprod(["unit_to_add", "price"], from_=df),
)

df = df.with_columns(
    fraction=(el.col("total_price") / (el.cell(total_df["total"][0]))),
    ideal_fraction=el.lit([0.5, 0.15, 0.15, 0.09, 0.11]),
    delta=(
        el.cell(total_df["total"][0]) * (el.col("ideal_fraction") - el.col("fraction"))
    ),
    delta_in_units=el.col("delta") / el.col("price"),
)

(
    df.style.fmt_integer(columns=["unit"])
    .fmt_currency(columns=["price", "total_price", "delta"])
    .fmt_percent(columns=["fraction", "ideal_fraction"])
)


df = df.select(columns)
for i in range(df.height):
    df["unit_to_add"][i].is_editable = True

total_df.style.fmt_currency(columns=["total", "cash"])
total_df["cash"][0].is_editable = True

sheet_styler = el.SheetStyler().cols_width({i: 150 for i in range(10)})


el.display([(df, (0, 0)), (total_df, (6, 0))], sheet_styler=sheet_styler)
