import excelify as el


def assert_str(expected, actual):
    assert expected.strip() == actual.strip()


def test_excel_load_save(tmp_path):
    df = el.ExcelFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    el.to_excel(
        [(df, (0, 0))], path=tmp_path / "test.xlsx", index_path=tmp_path / "index.json"
    )
    [df_loaded] = el.of_excel(
        path=tmp_path / "test.xlsx", index_path=tmp_path / "index.json"
    )
    assert_str(
        str(df),
        """
shape: (3, 2)
+---+-------+-------+
|   | x (A) | y (B) |
+---+-------+-------+
| 1 | 1.00  | 4.00  |
| 2 | 2.00  | 5.00  |
| 3 | 3.00  | 6.00  |
+---+-------+-------+
""",
    )
    assert_str(
        str(df_loaded),
        """
shape: (3, 2)
+---+-------+-------+
|   | x (A) | y (B) |
+---+-------+-------+
| 1 | 1.00  | 4.00  |
| 2 | 2.00  | 5.00  |
| 3 | 3.00  | 6.00  |
+---+-------+-------+
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
| 1 | 1.00  | 2.00  | 3.00  |
| 2 | 4.00  | 5.00  | 6.00  |
+---+-------+-------+-------+
""",
    )
