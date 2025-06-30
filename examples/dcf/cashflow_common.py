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
