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
