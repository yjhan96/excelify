import excelify as el


def assert_str(expected, actual):
    assert expected.strip() == actual.strip()


def test_excel_load_save(tmp_path):
    df = el.ExcelFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    df = df.with_columns(
        (el.col("x") * el.col("y") - el.col("x")).alias("z"),
    )
    el.to_excel(
        [(df, (0, 0))], path=tmp_path / "test.xlsx", index_path=tmp_path / "index.json"
    )
    [df_loaded] = el.of_excel(
        path=tmp_path / "test.xlsx", index_path=tmp_path / "index.json"
    )
    assert_str(
        str(df),
        """
shape: (3, 3)
+---+-------+-------+--------------+
|   | x (A) | y (B) |    z (C)     |
+---+-------+-------+--------------+
| 1 |   1   |   4   | A1 * B1 - A1 |
| 2 |   2   |   5   | A2 * B2 - A2 |
| 3 |   3   |   6   | A3 * B3 - A3 |
+---+-------+-------+--------------+
""",
    )
    assert_str(
        str(df_loaded),
        """
shape: (3, 3)
+---+-------+-------+--------------+
|   | x (A) | y (B) |    z (C)     |
+---+-------+-------+--------------+
| 1 |  1.0  |  4.0  | A1 * B1 - A1 |
| 2 |  2.0  |  5.0  | A2 * B2 - A2 |
| 3 |  3.0  |  6.0  | A3 * B3 - A3 |
+---+-------+-------+--------------+
""",
    )


def test_excel_load_save_agg_fn(tmp_path):
    df = el.ExcelFrame({"x": [1, 2], "y": [3, 4]})
    df = df.with_columns(x_sum=el.sum("x"), y_avg=el.average("y"))
    el.to_excel(
        [(df, (0, 0))], path=tmp_path / "test.xlsx", index_path=tmp_path / "index.json"
    )
    [df_loaded] = el.of_excel(
        path=tmp_path / "test.xlsx", index_path=tmp_path / "index.json"
    )
    assert_str(
        str(df),
        """
shape: (2, 4)
+---+-------+-------+------------+----------------+
|   | x (A) | y (B) | x_sum (C)  |   y_avg (D)    |
+---+-------+-------+------------+----------------+
| 1 |   1   |   3   | SUM(A1:A2) | AVERAGE(B1:B2) |
| 2 |   2   |   4   | SUM(A1:A2) | AVERAGE(B1:B2) |
+---+-------+-------+------------+----------------+
""",
    )
    assert_str(
        str(df_loaded),
        """
shape: (2, 4)
+---+-------+-------+------------+----------------+
|   | x (A) | y (B) | x_sum (C)  |   y_avg (D)    |
+---+-------+-------+------------+----------------+
| 1 |  1.0  |  3.0  | SUM(A1:A2) | AVERAGE(B1:B2) |
| 2 |  2.0  |  4.0  | SUM(A1:A2) | AVERAGE(B1:B2) |
+---+-------+-------+------------+----------------+
""",
    )


def test_of_csv(tmp_path):
    csv_content = """
x,y,z
1,2,3
4,5,6
"""
    with (tmp_path / "test.csv").open("w") as f:
        f.write(csv_content.strip())

    df = el.of_csv(path=tmp_path / "test.csv")
    assert_str(
        str(df),
        """
shape: (2, 3)
+---+-------+-------+-------+
|   | x (A) | y (B) | z (C) |
+---+-------+-------+-------+
| 1 |  1.0  |  2.0  |  3.0  |
| 2 |  4.0  |  5.0  |  6.0  |
+---+-------+-------+-------+
""",
    )
