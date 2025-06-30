import excelify as el

from historical_cashflow import historical_ufcf_df
from projected_cashflow import projected_ufcf_df

ufcf_df = el.concat([historical_ufcf_df, projected_ufcf_df])

# Once we fill out all the formulas for the table, we can define the cell's
# styles using `df.styles`.
# You can "chain" the styles setup like below.
(
    ufcf_df.style.display_horizontally()
    .fmt_number(
        columns=[
            "Sales per Square Foot",
            "COGS and OpEx per Square Foot",
            "Maintenance CapEx per Square Foot",
            "D&A per Square Foot",
            "Operating (EBIT) Margin",
            "Growth CapEx per New Square Foot",
        ],
        decimals=3,
    )
    .fmt_number(
        columns=[
            "Taxes, Excluding Effect of Interest",
            "Net Operating Profit After Tax (NOPAT)",
            "Deferred Taxes",
            "Annual Unlevered Free Cash Flow",
            "PV of Unlevered FCF",
        ]
    )
    .fmt_percent(
        columns=[
            "Retail Square Feet Growth Rate",
            "Sales per Square Foot Growth Rate",
            "COGS and OpEx per Square Foot Growth Rate",
            "Maintenance CapEx per Square Foot Growth Rate",
            "D&A per Square Foot Growth Rate",
            "Membership & Other Income Growth Rate",
            "Revenue Growth",
            "Depreciation & Amortization (% Revenue)",
            "Deferred Taxes (% Book Taxes)",
            "Other Operating Activities (% Revenue)",
            "Change in Working Capital (% Change in Revenue)",
            "Capital Expenditures (% Revenue)",
            "Annual Unlevered Free Cash Flow Growth Rate",
            "EBITDA Growth Rate",
            "Growth CapEx per New Square Foot Growth Rate",
        ]
    )
    .fmt_integer(
        columns=[
            "Retail Square Feet",
            "Net Sales",
            "Membership & Other Income",
            "Total Revenue",
            "Operating Income (EBIT)",
            "Depreciation & Amortization",
            "Other Operating Activities",
            "Change in Working Capital",
            "Capital Expenditures",
            "EBITDA",
        ]
    )
    .group_columns(
        [
            ("", ["years"]),
            ("", ["Retail Square Feet", "Retail Square Feet Growth Rate"]),
            ("", ["Sales per Square Foot", "Sales per Square Foot Growth Rate"]),
            (
                "",
                [
                    "COGS and OpEx per Square Foot",
                    "COGS and OpEx per Square Foot Growth Rate",
                ],
            ),
            (
                "",
                [
                    "Maintenance CapEx per Square Foot",
                    "Maintenance CapEx per Square Foot Growth Rate",
                ],
            ),
            ("", ["D&A per Square Foot", "D&A per Square Foot Growth Rate"]),
            (
                "",
                [
                    "Growth CapEx per New Square Foot",
                    "Growth CapEx per New Square Foot Growth Rate",
                ],
            ),
            ("", ["Membership & Other Income Growth Rate"]),
            (
                "Revenue:",
                [
                    "Net Sales",
                    "Membership & Other Income",
                    "Total Revenue",
                    "Revenue Growth",
                ],
            ),
            (
                "",
                ["Operating Income (EBIT)", "Operating (EBIT) Margin"],
            ),
            (
                "",
                ["Taxes, Excluding Effect of Interest"],
            ),
            ("", ["Net Operating Profit After Tax (NOPAT)"]),
            (
                "Adjustments for Non-Cash Charges:",
                [
                    "Depreciation & Amortization",
                    "Depreciation & Amortization (% Revenue)",
                ],
            ),
            ("", ["Deferred Taxes", "Deferred Taxes (% Book Taxes)"]),
            (
                "",
                [
                    "Other Operating Activities",
                    "Other Operating Activities (% Revenue)",
                ],
            ),
            (
                "",
                [
                    "Change in Working Capital",
                    "Change in Working Capital (% Change in Revenue)",
                ],
            ),
            ("", ["Capital Expenditures", "Capital Expenditures (% Revenue)"]),
            (
                "",
                [
                    "Annual Unlevered Free Cash Flow",
                    "Annual Unlevered Free Cash Flow Growth Rate",
                ],
            ),
            ("", ["Period", "PV of Unlevered FCF"]),
            ("", ["EBITDA", "EBITDA Growth Rate"]),
        ],
    )
    .rename_columns(
        {
            "Retail Square Feet Growth Rate": "Growth Rate:",
            "Sales per Square Foot Growth Rate": "Growth Rate:",
            "COGS and OpEx per Square Foot Growth Rate": "Growth Rate:",
            "Maintenance CapEx per Square Foot Growth Rate": "Growth Rate:",
            "D&A per Square Foot Growth Rate": "Growth Rate:",
            "Growth CapEx per New Square Foot Growth Rate": "Growth Rate:",
            "Depreciation & Amortization (% Revenue)": "% Revenue:",
            "Deferred Taxes (% Book Taxes)": "% Revenue:",
            "Other Operating Activities (% Revenue)": "% Revenue:",
            "Change in Working Capital (% Change in Revenue)": "% Change in Revenue:",
            "Capital Expenditures (% Revenue)": "% Revenue",
            "Annual Unlevered Free Cash Flow Growth Rate": "Growth Rate:",
            "EBITDA Growth Rate": "Growth Rate:",
        }
    )
    .value_color(
        columns=[
            "Retail Square Feet",
            "Net Sales",
            "Membership & Other Income",
            "Operating Income (EBIT)",
            "Depreciation & Amortization",
            "Other Operating Activities",
        ],
        rows=[0, 1, 2],
        color="blue",
    )
)
