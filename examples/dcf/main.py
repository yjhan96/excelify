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

from cashflow import ufcf_df
from constants import assumptions_df

import excelify as el

sheet_styler = el.SheetStyler().cols_width(
    {"A": 350} | {chr(ord("B") + i): 100 for i in range(13)}
)

el.display([(assumptions_df, (0, 0)), (ufcf_df, (6, 0))], sheet_styler=sheet_styler)
