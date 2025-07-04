import excelify as el

# Option parameters table
option_params = el.ExcelFrame.empty(
    columns=["parameter", "value"],
    height=3,
)

option_params = option_params.with_columns(
    parameter=el.lit(["Strike Price", "Premium Paid", "Current Stock Price"]),
    value=el.lit([100.0, 5.0, 105.0]),
)

# Format option parameters
(
    option_params.style
    .fmt_currency(columns=["value"])
)

# Make parameters editable
option_params["value"][0].is_editable = True
option_params["value"][1].is_editable = True
option_params["value"][2].is_editable = True

# Call option payoff table
option_table = el.ExcelFrame.empty(
    columns=["stock_price", "call_intrinsic", "call_profit_loss", "delta"],
    height=21,  # Stock prices from $80 to $120
)

option_table = option_table.with_columns(
    stock_price=el.map(
        lambda idx: el.cell(option_params["value"][2]) + (idx - 10) * 2.0  # Center at middle row (idx=10), +/- $2 per row
    ),
    call_intrinsic=el.map(
        lambda idx: el.max(el.col("stock_price") - el.cell(option_params["value"][0]), el.lit(0.0))
    ),
    call_profit_loss=el.map(
        lambda idx: el.col("call_intrinsic") - el.cell(option_params["value"][1])
    ),
    delta=el.map(
        lambda idx: el.if_(el.col("stock_price") > el.cell(option_params["value"][0]), el.lit(1.0), el.lit(0.0))
    ),
)

# Format as currency and percentage
(
    option_table.style
    .fmt_currency(columns=["stock_price", "call_intrinsic", "call_profit_loss"])
    .fmt_percent(columns=["delta"])
)

sheet_styler = el.SheetStyler().cols_width({"A": 120, "B": 120, "C": 120, "D": 80})

el.display([(option_params, (0, 0)), (option_table, (5, 0))], sheet_styler=sheet_styler)
