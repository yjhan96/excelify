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
