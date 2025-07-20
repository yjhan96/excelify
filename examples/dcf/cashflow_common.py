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

import excelify as el


def growth_rate(col: str, *, col_name=None, prev_cell: el.Cell | None = None):
    """Given a column `col`, return an expression that computes the growth rate
    from the previous row.

    If `col_name` is None, it'll name the expression as `{col} Growth Rate`.
    User can override this name by explicitly specifying the name.

    By default, the first row of the column will return error as there's no
    previous cell. If user would like to specify the previous cell for the
    first row, they can specify the cell in `prev_cell`.
    """
    if col_name is None:
        col_name = f"{col} Growth Rate"

    def fn(idx):
        if idx == 0 and prev_cell is not None:
            return el.col(col) / el.cell(prev_cell) - 1
        else:
            return (el.col(col) / el.col(col).prev(1) - 1).alias(col_name)

    return el.map(fn).alias(col_name)


def percent_revenue(col: str):
    """Given a column `col`, return an expression `{col} (% Revenue)` that
    represents the percent of the 'Total Revenue' column.
    """
    return (el.col(col) / el.col("Total Revenue")).alias(f"{col} (% Revenue)")
