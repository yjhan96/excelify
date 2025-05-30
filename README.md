## Excelify: Create Excel spreadsheets using DataFrame-like API

Excelify is a DataFrame-like framework that lets users create Excel spreadsheets.

To learn more, read Getting Started. TODO: Add a link.

## Example
```python
>>> import excelify as el
>>> df = el.ExcelFrame.empty(
...     columns=["year", "annual_investment", "annual_return", "compounded_amount"],
...     height=10,
... )
```
You can set a value for a single cell:
```python
>>> df["annual_return"][0] = 0.15
>>> df = df.with_columns(
...    el.lit([i for i in range(10)]).alias("year"),
...    (el.col("annual_return").prev(1)).alias("annual_return"),
... )
```
