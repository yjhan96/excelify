from lark import Lark, Transformer

from excelify._cell_expr import Add, CellExpr, CellRef, Constant, Div, Mult, Sub


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

    def cellref(self, args) -> CellExpr:
        (column_str, row_idx) = args
        cell_ref = self.cellpos_to_cellref(column_str, int(row_idx))
        return CellRef(cell_ref)

    def number(self, n) -> CellExpr:
        (n,) = n
        return Constant(float(n))


def create_parser(cellpos_to_cellref):
    return Lark(
        r"""
    ?excel_expr: SIGNED_NUMBER -> number
               | "="expr

    ?expr: SIGNED_NUMBER -> number
         | "(" expr ")"
         | expr "*" expr -> mult
         | expr "/" expr -> div
         | expr "+" expr -> plus
         | expr "-" expr -> minus
         | cellref
         | formulas

    formulas: "AVERAGE(" cellref ":" cellref ")" -> average_fn
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
