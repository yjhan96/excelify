import excelify as el

previous_tax_rates = [6858 / 20564, 4915 / 20116, 4281 / 11460]
assumptions_df = el.ExcelFrame(
    {
        "Company Name": ["Walmart Inc."],
        "Ticker": ["WMT"],
        "Current Share Price": [139.43],
        "Effective Tax Rate": [sum(previous_tax_rates) / len(previous_tax_rates)],
        "Last Fiscal Year": ["2021-01-31"],
    },
)

# TODO: Make this more ergonomic.
# assumptions_df["Company Name"].set_attributes({"bgcolor": "blue"})
# assumptions_df["Current Share Price"].set_attributes({"bgcolor": "#000"})

(
    assumptions_df.style.fmt_currency(columns=["Current Share Price"])
    .fmt_number(columns=["Effective Tax Rate"], decimals=2)
    .display_horizontally()
)
