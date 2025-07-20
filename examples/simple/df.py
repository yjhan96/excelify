import excelify as el

length = 20

df = el.ExcelFrame.empty(
    columns=["year", "annual_return", "compounded_amount", "annual_investment", "total_return"],
    height=length,
)
df = df.with_columns(
    year=el.lit([i + 1 for i in range(length)]),
    annual_return=el.map(
        lambda idx: 0.15 if idx == 0 else el.col("annual_return").prev(1)
    ),
    annual_investment=el.map(
        lambda idx: 120.0 if idx == 0 else el.col("annual_investment").prev(1)
    ),
    compounded_amount=el.map(
        lambda idx: 100.0
        if idx == 0
        else (
            el.col("compounded_amount").prev(1) * (1.0 + el.col("annual_return"))
            + el.col("annual_investment")
        )
    ),
    total_return=el.map(
        lambda idx: (el.col("compounded_amount") - el.cell(df["compounded_amount"][0])) / el.cell(df["compounded_amount"][0])
    ),
)

df = df.select(["year", "annual_investment", "annual_return", "compounded_amount", "total_return"])


# TODO: Should this go under style?
df["annual_investment"][0].is_editable = True
df["annual_return"][0].is_editable = True
df["compounded_amount"][0].is_editable = True
(
    df.style.fmt_integer(columns=["year"])
    .fmt_currency(columns=["annual_investment", "compounded_amount"], accounting=True)
    .fmt_percent(columns=["annual_return", "total_return"])
)

sheet_styler = el.SheetStyler().cols_width({"B": 150, "C": 110, "D": 150, "E": 120})

el.display([(df, (0, 0))], sheet_styler=sheet_styler)
