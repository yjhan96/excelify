import excelify as el


def assert_str(expected, actual):
    assert expected.strip() == actual.strip()


def test_basic_precedence():
    """Test that operator precedence works correctly without unnecessary parentheses."""
    df = el.ExcelFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
    df = df.with_columns(
        (el.col("x") * el.col("y") - el.col("x")).alias("z"),
    )

    # Should be: A1 * B1 - A1 (multiplication before subtraction, no extra parentheses)
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


def test_arithmetic_precedence():
    """Test various arithmetic operator precedence combinations."""
    df = el.ExcelFrame({"x": [1], "y": [2], "z": [3]})
    df = df.with_columns(
        add_mult=(el.col("x") + el.col("y") * el.col("z")),  # Should be: x + y * z
        paren_mult=(
            (el.col("x") + el.col("y")) * el.col("z")
        ),  # Should be: (x + y) * z
        pow_mult=(el.col("x") ** el.col("y") * el.col("z")),  # Should be: x ^ y * z
        mult_pow=(el.col("x") * el.col("y") ** el.col("z")),  # Should be: x * y ^ z
    )

    assert_str(
        str(df),
        """
shape: (1, 7)
+---+-------+-------+-------+--------------+----------------+--------------+--------------+
|   | x (A) | y (B) | z (C) | add_mult (D) | paren_mult (E) | pow_mult (F) | mult_pow (G) |
+---+-------+-------+-------+--------------+----------------+--------------+--------------+
| 1 |   1   |   2   |   3   | A1 + B1 * C1 | (A1 + B1) * C1 | A1 ^ B1 * C1 | A1 * B1 ^ C1 |
+---+-------+-------+-------+--------------+----------------+--------------+--------------+
""",
    )


def test_subtraction_division_precedence():
    """Test subtraction and division precedence."""
    df = el.ExcelFrame({"x": [10], "y": [2], "z": [3]})
    df = df.with_columns(
        sub_mult=(el.col("x") - el.col("y") * el.col("z")),  # Should be: x - y * z
        div_add=(el.col("x") / el.col("y") + el.col("z")),  # Should be: x / y + z
        sub_div=(el.col("x") - el.col("y") / el.col("z")),  # Should be: x - y / z
    )

    assert_str(
        str(df),
        """
shape: (1, 6)
+---+-------+-------+-------+--------------+--------------+--------------+
|   | x (A) | y (B) | z (C) | sub_mult (D) | div_add (E)  | sub_div (F)  |
+---+-------+-------+-------+--------------+--------------+--------------+
| 1 |  10   |   2   |   3   | A1 - B1 * C1 | A1 / B1 + C1 | A1 - B1 / C1 |
+---+-------+-------+-------+--------------+--------------+--------------+
""",
    )


def test_explicit_parentheses_preserved():
    """Test that explicit parentheses are preserved when they change precedence."""
    df = el.ExcelFrame({"x": [1], "y": [2], "z": [3]})
    df = df.with_columns(
        # Force addition before multiplication with explicit parentheses
        forced_add_mult=((el.col("x") + el.col("y")) * el.col("z")),
        # Force subtraction before division with explicit parentheses
        forced_sub_div=((el.col("x") - el.col("y")) / el.col("z")),
    )

    assert_str(
        str(df),
        """
shape: (1, 5)
+---+-------+-------+-------+---------------------+--------------------+
|   | x (A) | y (B) | z (C) | forced_add_mult (D) | forced_sub_div (E) |
+---+-------+-------+-------+---------------------+--------------------+
| 1 |   1   |   2   |   3   |   (A1 + B1) * C1    |   (A1 - B1) / C1   |
+---+-------+-------+-------+---------------------+--------------------+
""",
    )


def test_nested_expressions():
    """Test nested expressions with multiple precedence levels."""
    df = el.ExcelFrame({"a": [1], "b": [2], "c": [3], "d": [4]})
    df = df.with_columns(
        # Complex expression: a + b * c ^ d should be: a + b * (c ^ d)
        complex_expr=(el.col("a") + el.col("b") * el.col("c") ** el.col("d")),
    )

    assert_str(
        str(df),
        """
shape: (1, 5)
+---+-------+-------+-------+-------+-------------------+
|   | a (A) | b (B) | c (C) | d (D) | complex_expr (E)  |
+---+-------+-------+-------+-------+-------------------+
| 1 |   1   |   2   |   3   |   4   | A1 + B1 * C1 ^ D1 |
+---+-------+-------+-------+-------+-------------------+
""",
    )
