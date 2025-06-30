from cashflow import ufcf_df
from constants import assumptions_df

import excelify as el

sheet_styler = el.SheetStyler().cols_width(
    {"A": 350} | {chr(ord("B") + i): 100 for i in range(13)}
)

el.display([(assumptions_df, (0, 0)), (ufcf_df, (6, 0))], sheet_styler=sheet_styler)
