import excelify as el

length = 20

df = el.ExcelFrame.empty(
    columns=["year", "annual_return", "compounded_amount", "annual_investment"],
    height=length,
)
df = df.with_columns(
    year=el.lit([i + 1 for i in range(length)]),
    annual_return=el.Map(
        lambda idx: 0.15 if idx == 0 else el.col("annual_return").prev(1)
    ),
    annual_investment=el.Map(
        lambda idx: 120.0 if idx == 0 else el.col("annual_investment").prev(1)
    ),
    compounded_amount=el.Map(
        lambda idx: 100.0
        if idx == 0
        else (
            el.col("compounded_amount").prev(1) * (1.0 + el.col("annual_return"))
            + el.col("annual_investment")
        )
    ),
)

df = df.select(["year", "annual_investment", "annual_return", "compounded_amount"])


# TODO: Should this go under style?
df["annual_investment"][0].is_editable = True
df["annual_return"][0].is_editable = True
df["compounded_amount"][0].is_editable = True
(
    df.style.fmt_integer(columns=["year"])
    .fmt_currency(columns=["annual_investment", "compounded_amount"], accounting=True)
    .fmt_percent(columns=["annual_return"])
    .value_color(columns=["annual_investment"], color="green")
)

df2 = el.ExcelFrame.empty(columns=["x", "y"], height=10)
df2 = df2.with_columns(
    x=el.col("annual_investment", from_=df), y=el.col("compounded_amount", from_=df)
)

(
    df2.style.fmt_integer(columns=["y"])
)


sheet_styler = el.SheetStyler().cols_width({"B": 150, "C": 110, "D": 150})

el.display([(df, (0, 0)), (df2, (0, len(df.columns)))], sheet_styler=sheet_styler)
