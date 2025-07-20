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

from cashflow_common import growth_rate, percent_revenue
from constants import assumptions_df

years = [str(year) for year in range(2019, 2022)]

# First, let's define a list of columns.

# We'd like to know some key metrics based on per retail square foot basis for
# Walmart DCF. We define the list of such metrics below.
sqft_columns = [
    "Retail Square Feet",
    "Sales per Square Foot",
    "COGS and OpEx per Square Foot",
    "Maintenance CapEx per Square Foot",
    "D&A per Square Foot",
    "Growth CapEx per New Square Foot",
]

# Then, we'd like to know the growth rate of each metrics on year over year
# (YoY) basis, so we define its growth rate column as well.
sqft_with_growth_rate_columns = [[col, f"{col} Growth Rate"] for col in sqft_columns]
sqft_with_growth_rate_columns = [
    col for cols in sqft_with_growth_rate_columns for col in cols
] + ["Membership & Other Income Growth Rate"]

# Next, we define columns to help understand both revenues and cash flows.
revenue_columns = [
    "Net Sales",
    "Membership & Other Income",
    "Total Revenue",
    "Revenue Growth",
]
cash_flow_columns = [
    "Operating Income (EBIT)",
    "Operating (EBIT) Margin",
    "Taxes, Excluding Effect of Interest",
    "Net Operating Profit After Tax (NOPAT)",
    "Depreciation & Amortization",
    "Depreciation & Amortization (% Revenue)",
    "Deferred Taxes",
    "Deferred Taxes (% Book Taxes)",
    "Other Operating Activities",
    "Other Operating Activities (% Revenue)",
    "Change in Working Capital",
    "Change in Working Capital (% Change in Revenue)",
    "Capital Expenditures",
    "Capital Expenditures (% Revenue)",
    "Annual Unlevered Free Cash Flow",
    "Annual Unlevered Free Cash Flow Growth Rate",
    "Period",
    "PV of Unlevered FCF",
    "EBITDA",
    "EBITDA Growth Rate",
]

columns = (
    ["years"] + sqft_with_growth_rate_columns + revenue_columns + cash_flow_columns
)

# Now that we specified all the columns, we create an empty `ExcelFrame` table.
historical_ufcf_df = el.ExcelFrame.empty(columns=columns, height=len(years))


# First, let's fill in some constant values. Assume that we retrieved
# these values from a different data source (e.g. Accounting, 10-K, etc.).

historical_ufcf_df = historical_ufcf_df.with_columns(
    el.lit(years).alias("years"),
    el.lit([1_129, 1_129, 1_121]).alias("Retail Square Feet"),
    el.lit([510_329.0, 519_926.0, 555_233.0]).alias("Net Sales"),
    el.lit([4076.0, 4038.0, 3918.0]).alias("Membership & Other Income"),
    el.lit([21_957.0, 20_568.0, 22_548.0]).alias("Operating Income (EBIT)"),
    el.lit([10_678.0, 10_987.0, 11_152.0]).alias("Depreciation & Amortization"),
)

# Then, we can define per retail sqaure foot metrics:
historical_ufcf_df = historical_ufcf_df.with_columns(
    (el.col("Net Sales") / el.col("Retail Square Feet")).alias("Sales per Square Foot"),
    (
        (el.col("Net Sales") - el.col("Operating Income (EBIT)"))
        / el.col("Retail Square Feet")
    ).alias("COGS and OpEx per Square Foot"),
    # lambda functions are anonymous functions that will take index of the row
    # as an input (`idx` in this case) and output an expression for such row.
    #
    # In plain English, the below function means "For the 0th row, the cell's
    # expression will be negative CapEx divided by 1158, and for the rest, it'll be
    # negative CapEx divided by prevoius row's Retail Square Feet", as Maintenance
    # CapEx is based on previous year's retail square feet.
    el.map(
        lambda idx: -el.col("Capital Expenditures") / 1158
        if idx == 0
        else -el.col("Capital Expenditures") / el.col("Retail Square Feet").prev(1)
    ).alias("Maintenance CapEx per Square Foot"),
    (el.col("Depreciation & Amortization") / el.col("Retail Square Feet")).alias(
        "D&A per Square Foot"
    ),
)

# We now define the growth rate metrics. We'll use the helper function
# `growth_rate` to define the expression for below columns.
historical_ufcf_df = historical_ufcf_df.with_columns(
    *(
        growth_rate(c)
        for c in sqft_columns
        if c not in ["Growth CapEx per New Square Foot"]
    )
)

# Now, it's time to define revenue and cash flow-related columns.
# Again, we first define some constants first:
historical_ufcf_df = historical_ufcf_df.with_columns(
    el.lit([1_734, 1_981, 1_521]).alias("Other Operating Activities"),
    el.lit([295, -327, 7972]).alias("Change in Working Capital"),
    el.lit([-10_344, -10_705, -10_264]).alias("Capital Expenditures"),
    el.lit(
        [
            el.constant(-499) / el.constant(4281),
            el.constant(320) / el.constant(4915),
            el.constant(1911) / el.constant(6858),
        ]
    ).alias("Deferred Taxes (% Book Taxes)"),
)

# We can now define the rest by writing down the formula for each term
# (e.g. Total revenue is the sume of net sales and membership & other income).
historical_ufcf_df = historical_ufcf_df.with_columns(
    (el.col("Net Sales") + el.col("Membership & Other Income")).alias("Total Revenue"),
    growth_rate("Total Revenue", col_name="Revenue Growth"),
    (el.col("Operating Income (EBIT)") / el.col("Total Revenue")).alias(
        "Operating (EBIT) Margin"
    ),
    (
        -el.col("Operating Income (EBIT)")
        * el.cell(assumptions_df["Effective Tax Rate"][0])
    ).alias("Taxes, Excluding Effect of Interest"),
    (
        el.col("Operating Income (EBIT)")
        + el.col("Taxes, Excluding Effect of Interest")
    ).alias("Net Operating Profit After Tax (NOPAT)"),
    percent_revenue("Depreciation & Amortization"),
    (
        -el.col("Deferred Taxes (% Book Taxes)")
        * el.col("Taxes, Excluding Effect of Interest")
    ).alias("Deferred Taxes"),
    percent_revenue("Other Operating Activities"),
    (
        el.col("Change in Working Capital")
        / (el.col("Total Revenue") - el.col("Total Revenue").prev(1))
    ).alias("Change in Working Capital (% Change in Revenue)"),
    percent_revenue("Capital Expenditures"),
    (
        el.col("Net Operating Profit After Tax (NOPAT)")
        + el.col("Depreciation & Amortization")
        + el.col("Deferred Taxes")
        + el.col("Other Operating Activities")
        + el.col("Change in Working Capital")
        + el.col("Capital Expenditures")
    ).alias("Annual Unlevered Free Cash Flow"),
    growth_rate("Annual Unlevered Free Cash Flow"),
    (el.col("Operating Income (EBIT)") + el.col("Depreciation & Amortization")).alias(
        "EBITDA"
    ),
    growth_rate("EBITDA"),
).select(columns)
