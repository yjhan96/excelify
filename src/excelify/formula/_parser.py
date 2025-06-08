from lark import Lark, Transformer

from excelify._cell import Cell
from excelify._cell_expr import (
    Add,
    AverageCellsRef,
    CellExpr,
    CellRef,
    Constant,
    Div,
    Mult,
    Sub,
    SumCellsRef,
)


class TreeToCellExpr(Transformer):
    def __init__(self, cellpos_to_cellref):
        super().__init__()
        self.cellpos_to_cellref = cellpos_to_cellref

    def plus(self, exprs) -> CellExpr:
        expr1, expr2 = exprs
        return Add(expr1, expr2)

    def minus(self, exprs) -> CellExpr:
        expr1, expr2 = exprs
        return Sub(expr1, expr2)

    def mult(self, exprs) -> CellExpr:
        expr1, expr2 = exprs
        return Mult(expr1, expr2)

    def div(self, exprs) -> CellExpr:
        expr1, expr2 = exprs
        return Div(expr1, expr2)

    def cellref_expr(self, args) -> CellExpr:
        (cell_ref,) = args
        df, col_idx, row_idx = cell_ref
        return CellRef(df[df.columns[col_idx]][row_idx])

    def cellref(self, args) -> Cell:
        (column_str, row_idx) = args
        return self.cellpos_to_cellref(column_str, int(row_idx))

    @staticmethod
    def _verify_agg_fn_range(from_cellref, to_cellref) -> None:
        from_cell_df, from_col_idx, _ = from_cellref
        to_cell_df, to_col_idx, _ = to_cellref

        if not (from_cell_df == to_cell_df and from_col_idx == to_col_idx):
            raise ValueError(
                "Received different column name for start and end cell. "
                "Excelfiy currently doesn't support aggregate function "
                f"across columns. From: {from_cell_df.columns[from_col_idx]}, "
                f"To:{to_cell_df.columns[to_col_idx]}"
            )

    def average_fn(self, args) -> CellExpr:
        (from_cellref, to_cellref) = args
        TreeToCellExpr._verify_agg_fn_range(from_cellref, to_cellref)
        from_cell_df, from_col_idx, from_row_idx = from_cellref
        _, _, to_row_idx = to_cellref
        from_row_idx = min(from_row_idx, to_row_idx)
        to_row_idx = max(from_row_idx, to_row_idx)
        cells = [
            from_cell_df[from_cell_df.columns[from_col_idx]][row_idx]
            for row_idx in range(from_row_idx, to_row_idx + 1)
        ]
        return AverageCellsRef(cells)

    def sum_fn(self, args) -> CellExpr:
        (from_cellref, to_cellref) = args
        TreeToCellExpr._verify_agg_fn_range(from_cellref, to_cellref)
        from_cell_df, from_col_idx, from_row_idx = from_cellref
        _, _, to_row_idx = to_cellref
        from_row_idx = min(from_row_idx, to_row_idx)
        to_row_idx = max(from_row_idx, to_row_idx)
        cells = [
            from_cell_df[from_cell_df.columns[from_col_idx]][row_idx]
            for row_idx in range(from_row_idx, to_row_idx + 1)
        ]
        return SumCellsRef(cells)

    def number(self, n) -> CellExpr:
        (n,) = n
        return Constant(float(n))


def create_parser(cellpos_to_cellref):
    return Lark(
        r"""
    ?excel_expr: SIGNED_NUMBER -> number
               | "="expr

    ?expr: term

    ?term: term "+" factor -> plus
         | term "-" factor -> minus
         | factor

    ?factor: factor "*" primary -> mult
           | factor "/" primary -> div
           | primary

    ?primary: SIGNED_NUMBER -> number
            | "(" expr ")"
            | cellref -> cellref_expr
            | formulas

    ?formulas: "AVERAGE(" cellref ":" cellref ")" -> average_fn
            | "SUM(" cellref ":" cellref ")" -> sum_fn

    cellref: (UCASE_LETTER+)(SIGNED_NUMBER)

    %import common.SIGNED_NUMBER
    %import common.UCASE_LETTER
    %import common.WS
    %ignore WS
    """,
        start="excel_expr",
        parser="lalr",
        transformer=TreeToCellExpr(cellpos_to_cellref),
    )
