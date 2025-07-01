import excelify as el


def main():
    constant_df = el.ExcelFrame.empty(
        columns=["principal", "interest_rate", "num_payments", "recurring_payment"],
        height=1,
    )

    constant_df = constant_df.with_columns(
        principal=el.constant(500_000),
        interest_rate=el.constant(0.065) / el.constant(12),
        num_payments=el.constant(30) * el.constant(12),
        recurring_payment=(
            el.col("principal")
            * (
                (
                    el.col("interest_rate")
                    * (1 + el.col("interest_rate")) ** el.col("num_payments")
                )
                / ((1 + el.col("interest_rate")) ** el.col("num_payments") - 1.0)
            )
        ),
    )
    constant_df["principal"][0].is_editable = True
    constant_df["interest_rate"][0].is_editable = True

    payment_df = el.ExcelFrame.empty(
        columns=[
            "year",
            "interest",
            "principal",
            "remaining_balance",
            "fv_principal",
            "fv_recurring_payment",
            "remaining_balance_2",
        ],
        height=12 * 5,
    )

    initial_p = el.cell(constant_df["principal"][0])
    interest_rate = el.cell(constant_df["interest_rate"][0])
    recurring_payment = el.cell(constant_df["recurring_payment"][0])

    payment_df = payment_df.with_columns(
        (1 - el.col("remaining_balance") / initial_p).alias("% of initial principal"),
        year=el.lit([i for i in range(payment_df.height)]),
        interest=el.map(
            lambda idx: (initial_p if idx == 0 else el.col("remaining_balance").prev(1))
            * interest_rate
        ),
        principal=recurring_payment - el.col("interest"),
        remaining_balance=el.map(
            lambda idx: (initial_p if idx == 0 else el.col("remaining_balance").prev(1))
            - el.col("principal")
        ),
        fv_principal=initial_p * ((1 + interest_rate) ** (el.col("year") + 1)),
        fv_recurring_payment=(
            recurring_payment
            * ((1 + interest_rate) ** (el.col("year") + 1) - 1)
            / interest_rate
        ),
        remaining_balance_2=el.col("fv_principal") - el.col("fv_recurring_payment"),
    )

    (
        constant_df.style.fmt_currency(columns=["principal", "recurring_payment"])
        .fmt_percent(columns=["interest_rate"])
        .fmt_integer(columns=["num_payments"])
        .display_horizontally()
    )

    (
        payment_df.style.fmt_integer(columns=["year"])
        .fmt_currency(
            columns=[
                "interest",
                "principal",
                "remaining_balance",
                "fv_principal",
                "fv_recurring_payment",
                "remaining_balance_2",
            ]
        )
        .fmt_percent(columns=["% of initial principal"])
    )

    sheet_styler = el.SheetStyler().cols_width(
        {"A": 150, "B": 120, "C": 120, "D": 130, "E": 130, "F": 130, "G": 130, "H": 130}
    )

    el.display([(constant_df, (0, 0)), (payment_df, (5, 0))], sheet_styler=sheet_styler)


if __name__ == "__main__":
    main()
