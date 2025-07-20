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
from historical_cashflow import historical_ufcf_df

years = [str(year) for year in range(2022, 2032)]

projected_ufcf_df = el.ExcelFrame.empty(columns=historical_ufcf_df.columns, height=10)


def projected_value(col: str, growth_rate_col):
    def fn(idx):
        if idx == 0:
            return el.cell(historical_ufcf_df[col][-1]) * (1 + el.col(growth_rate_col))
        else:
            return el.col(col).prev(1) * (1 + el.col(growth_rate_col))

    return el.map(fn).alias(col)


def growth_capex_per_new_sqft_formula(idx):
    if idx == 0:
        return 150.0
    else:
        return el.col("Growth CapEx per New Square Foot").prev(1) * (
            1 + el.col("Growth CapEx per New Square Foot Growth Rate")
        )


def change_in_working_capital_formula(idx):
    if idx == 0:
        return el.col("Change in Working Capital (% Change in Revenue)") * (
            el.col("Total Revenue") - el.cell(historical_ufcf_df["Total Revenue"][-1])
        )
    else:
        return el.col("Change in Working Capital (% Change in Revenue)") * (
            el.col("Total Revenue") - el.col("Total Revenue").prev(1)
        )


def capital_expenditures_formula(idx):
    prev_retail_square_feet = (
        el.col("Retail Square Feet").prev(1)
        if idx > 0
        else el.cell(historical_ufcf_df["Retail Square Feet"][-1])
    )
    return -el.col(
        "Maintenance CapEx per Square Foot"
    ) * prev_retail_square_feet - el.col("Growth CapEx per New Square Foot") * (
        el.col("Retail Square Feet") - prev_retail_square_feet
    )


projected_ufcf_df = projected_ufcf_df.with_columns(
    el.lit(years).alias("years"),
)

projected_ufcf_df = projected_ufcf_df.with_columns(
    projected_value("Retail Square Feet", "Retail Square Feet Growth Rate"),
    el.lit([0.02, 0.02, 0.015, 0.015, 0.01, 0.01, 0.005, 0.005, 0.005, 0.005]).alias(
        "Retail Square Feet Growth Rate"
    ),
    projected_value("Sales per Square Foot", "Sales per Square Foot Growth Rate"),
    el.lit([0.03, 0.03, 0.025, 0.025, 0.02, 0.02, 0.015, 0.015, 0.01, 0.01]).alias(
        "Sales per Square Foot Growth Rate"
    ),
    projected_value(
        "COGS and OpEx per Square Foot", "COGS and OpEx per Square Foot Growth Rate"
    ),
    el.lit([0.03, 0.03, 0.025, 0.025, 0.02, 0.02, 0.015, 0.015, 0.01, 0.01]).alias(
        "COGS and OpEx per Square Foot Growth Rate"
    ),
    projected_value(
        "Maintenance CapEx per Square Foot",
        "Maintenance CapEx per Square Foot Growth Rate",
    ),
    el.lit([0.03, 0.03, 0.025, 0.025, 0.02, 0.02, 0.015, 0.015, 0.01, 0.01]).alias(
        "Maintenance CapEx per Square Foot Growth Rate"
    ),
    projected_value("D&A per Square Foot", "D&A per Square Foot Growth Rate"),
    el.lit([0.025, 0.025, 0.02, 0.02, 0.015, 0.015, 0.01, 0.01, 0.008, 0.008]).alias(
        "D&A per Square Foot Growth Rate"
    ),
    el.map(growth_capex_per_new_sqft_formula).alias("Growth CapEx per New Square Foot"),
    el.lit([None, 0.03, 0.03, 0.025, 0.025, 0.02, 0.02, 0.015, 0.015, 0.01]).alias(
        "Growth CapEx per New Square Foot Growth Rate"
    ),
    el.lit([0.03, 0.03, 0.025, 0.025, 0.02, 0.02, 0.015, 0.015, 0.01, 0.01]).alias(
        "Membership & Other Income Growth Rate"
    ),
)

editable_columns = [
    "Retail Square Feet Growth Rate",
    "Sales per Square Foot Growth Rate",
    "COGS and OpEx per Square Foot Growth Rate",
    "Maintenance CapEx per Square Foot Growth Rate",
    "D&A per Square Foot Growth Rate",
    "Growth CapEx per New Square Foot Growth Rate",
    "Membership & Other Income Growth Rate",
]

for col_name in editable_columns:
    for cell in projected_ufcf_df[col_name]:
        cell.is_editable = True

projected_ufcf_df["Growth CapEx per New Square Foot Growth Rate"][0].is_editable = False
projected_ufcf_df["Growth CapEx per New Square Foot"][0].is_editable = True

projected_ufcf_df = projected_ufcf_df.with_columns(
    (el.col("Retail Square Feet") * el.col("Sales per Square Foot")).alias("Net Sales"),
    projected_value(
        "Membership & Other Income", "Membership & Other Income Growth Rate"
    ),
)

projected_ufcf_df = projected_ufcf_df.with_columns(
    (el.col("Net Sales") + el.col("Membership & Other Income")).alias("Total Revenue"),
    growth_rate(
        "Total Revenue",
        col_name="Revenue Growth",
        prev_cell=historical_ufcf_df["Total Revenue"][-1],
    ),
    (
        el.col("Net Sales")
        - el.col("COGS and OpEx per Square Foot") * el.col("Retail Square Feet")
    ).alias("Operating Income (EBIT)"),
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
    (el.col("Retail Square Feet") * el.col("D&A per Square Foot")).alias(
        "Depreciation & Amortization"
    ),
    percent_revenue("Depreciation & Amortization"),
    (
        -el.col("Deferred Taxes (% Book Taxes)")
        * el.col("Taxes, Excluding Effect of Interest")
    ).alias("Deferred Taxes"),
    el.lit([0.075, 0.07, 0.065, 0.06, 0.055, 0.05, 0.05, 0.05, 0.05, 0.05]).alias(
        "Deferred Taxes (% Book Taxes)"
    ),
    (el.col("Total Revenue") * el.col("Other Operating Activities (% Revenue)")).alias(
        "Other Operating Activities"
    ),
    (
        el.average("Other Operating Activities (% Revenue)", from_=historical_ufcf_df)
    ).alias("Other Operating Activities (% Revenue)"),
    el.map(change_in_working_capital_formula).alias("Change in Working Capital"),
    el.lit([0.1, 0.095, 0.09, 0.085, 0.08, 0.075, 0.075, 0.075, 0.075, 0.075]).alias(
        "Change in Working Capital (% Change in Revenue)"
    ),
    el.map(capital_expenditures_formula).alias("Capital Expenditures"),
    percent_revenue("Capital Expenditures"),
    (
        el.col("Net Operating Profit After Tax (NOPAT)")
        + el.col("Depreciation & Amortization")
        + el.col("Deferred Taxes")
        + el.col("Other Operating Activities")
        + el.col("Change in Working Capital")
        + el.col("Capital Expenditures")
    ).alias("Annual Unlevered Free Cash Flow"),
    growth_rate(
        "Annual Unlevered Free Cash Flow",
        prev_cell=historical_ufcf_df["Annual Unlevered Free Cash Flow"][-1],
    ),
    el.map(lambda idx: 1 if idx == 0 else el.col("Period").prev(1) + 1).alias("Period"),
    (
        el.col("Annual Unlevered Free Cash Flow") / ((1 + 0.04365) ** el.col("Period"))
    ).alias("PV of Unlevered FCF"),
    (el.col("Operating Income (EBIT)") + el.col("Depreciation & Amortization")).alias(
        "EBITDA"
    ),
    growth_rate("EBITDA", prev_cell=historical_ufcf_df["EBITDA"][-1]),
)

editable_columns = [
    "Deferred Taxes (% Book Taxes)",
    "Change in Working Capital (% Change in Revenue)",
]

for col_name in editable_columns:
    for cell in projected_ufcf_df[col_name]:
        cell.is_editable = True

projected_ufcf_df["Period"][0].is_editable = True
