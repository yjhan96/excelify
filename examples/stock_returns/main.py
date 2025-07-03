import excelify as el

# Assumptions table
assumptions_df = el.ExcelFrame.empty(
    columns=["parameter", "value"],
    height=2,
)

assumptions_df = assumptions_df.with_columns(
    parameter=el.lit(["Initial Investment", "Annual Return"]),
    value=el.lit([10000.0, 0.08]),
)

# Format assumptions table
(
    assumptions_df.style
    .fmt_currency(columns=["value"], rows=[0])
    .fmt_percent(columns=["value"], rows=[1])
)

# Make assumptions editable
assumptions_df["value"][0].is_editable = True
assumptions_df["value"][1].is_editable = True

# Investment projection table
projection_df = el.ExcelFrame.empty(
    columns=["year", "investment_value"],
    height=16,  # 15 years + starting year
)

projection_df = projection_df.with_columns(
    year=el.lit([2025 + i for i in range(16)]),
    investment_value=el.Map(
        lambda idx: el.cell(assumptions_df["value"][0]) if idx == 0 else el.col("investment_value").prev(1) * (1.0 + el.cell(assumptions_df["value"][1]))
    ),
)

# Format investment values as currency
projection_df.style.fmt_currency(columns=["investment_value"])

sheet_styler = el.SheetStyler().cols_width({"A": 120, "B": 150})

el.display([(assumptions_df, (0, 0)), (projection_df, (4, 0))], sheet_styler=sheet_styler)
