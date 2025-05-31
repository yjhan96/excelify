## Excelify: Create Excel spreadsheets using DataFrame-like API

Excelify is a DataFrame-like library that lets users create Excel spreadsheets.

To learn more, read Getting Started. TODO: Add a link.

## Example
We'll create a table that demonstrates compounded interest.
We first define an "emtpy table" using `el.ExcelFrame`:
```python
>>> import excelify as el
>>> df = el.ExcelFrame.empty(
...     columns=["year", "boy_amount", "annual_return", "eoy_amount"],
...     height=3,
... )
```

Excelify has a Polars-like API that lets you define the formula for all the
cells in a given column. For example, we can define static integer value
representing the number of years elapsed using `el.lit()`:

```python
>>> df = df.with_columns(
...    el.lit([i for i in range(3)]).alias("year"),
... )
```

However, unlike DataFrame, you can define a formula that'll be evaluated
lazily, just like Excel spreadsheets.

For example, suppose you'd like to define annual return to be 10% every year.
You can either use above `el.lit` function, or you can define a static value on
the first row cell and make subsequent rows refer to the previous row's value
using `el.Map` and `el.col().prev(1)`:

```python
>>> df = df.with_columns(
...     el.Map(
...         lambda idx: 0.10
...         if idx == 0
...         else el.col("annual_return").prev(1)
...     ).alias("annual_return")
... )
```
This way, you can edit only the first row cell of `annual_return` to change the
annual return value for all the years.

Similarly, you can define the amount of money in the beginning and end of the
year as follows:

```python
>>> df = df.with_columns(
...     el.Map(
...         lambda idx: 100.0
...         if idx == 0
...         else el.col("eoy_amount").prev(1)
...     ).alias("boy_amount"),
...     (el.col("boy_amount") * (1.0 + el.col("annual_return"))).alias("eoy_amount"),
... )
```

If you print `df`, you'll get the following:
```python
>>> df
```

Unlike DataFrame, ExcelFrame stores the formula of the cell by default. To see
numerical values, you can call `df.evaluate()` - it'll return a new ExcelFrame
where each cell will store the computed value of the formula in `df`:

```python
>>> df.evaluate()
```

To export the ExcelFrame to excel, simply call `df.to_excel()`.
