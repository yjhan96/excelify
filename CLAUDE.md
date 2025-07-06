# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Excelify is a DataFrame-like Python library that creates Excel spreadsheets with formula support. It allows users to define cell formulas that are evaluated lazily, similar to Excel, while providing a Polars-like API for column operations.

### Core Architecture

The library is structured around several key components:

- **ExcelFrame** (`_excelframe.py`): The main DataFrame-like container that holds cells and manages their relationships
- **Cell** (`_cell.py`): Individual spreadsheet cells that contain expressions and track dependencies
- **CellExpr** (`_cell_expr.py`): Abstract base for cell expressions (formulas) with concrete implementations for arithmetic operations, cell references, and functions
- **Expr** (`_expr.py`): Column-level expressions that generate cell expressions when applied to ExcelFrame rows
- **Formula Parser** (`formula/_parser.py`): Lark-based parser for Excel formula syntax
- **CellMapping** (`_cell_mapping.py`): Maps between cell positions and Excel-style references (A1, B2, etc.)

### Key Design Patterns

- **Lazy Evaluation**: Formulas are stored as expressions and evaluated on demand, similar to Excel
- **Dependency Tracking**: Cells automatically track their dependencies for proper evaluation order
- **Column-wise Operations**: Operations are applied to entire columns, generating appropriate cell formulas
- **Excel Compatibility**: Output maintains Excel formula syntax and can be exported to .xlsx files

## Development Commands

### Testing
```bash
pytest test/
```

### Type Checking
The project uses Pyright for type checking:
```bash
pyright
```

### Pre-commit Hooks
The project uses pre-commit hooks for quality checks:
```bash
pre-commit install
pre-commit run --all-files
```

### Documentation
Build documentation with MkDocs:
```bash
mkdocs serve  # Local development server
mkdocs build  # Build static site
```

### Package Management
Uses uv for dependency management:
```bash
uv sync      # Install/update dependencies
uv add <pkg> # Add new dependency
```

## Working with the Codebase

### Expression System
- Column expressions (`Expr`) generate cell expressions (`CellExpr`) when applied to rows
- Cell expressions support arithmetic operations and maintain dependency graphs
- Use `el.col("column_name")` to reference columns and `el.lit(value)` for constants
- When referencing cells from other ExcelFrames, use `el.cell(other_frame["column"][row])`
- Constants in expressions don't need `el.lit()` wrapping - use them directly (e.g., `1.0 + el.cell(...)`)
- Cross-frame references: `el.col("column", from_=other_frame)` for column references

### Adding New Functions
1. Add the cell-level implementation in `_cell_expr.py` (e.g., `SumCellsRef`, `AverageCellsRef`)
2. Add column-level wrapper in `_expr.py` if needed
3. Update the formula parser in `formula/_parser.py` for Excel syntax support
4. Export new functions in `__init__.py`

### Testing Patterns
Tests use pytest and focus on:
- Formula generation and evaluation
- Excel file round-trip compatibility
- Expression parsing and dependency tracking

Run individual tests:
```bash
pytest test/test_load_and_save.py::test_excel_load_save -v
```

### Cell Reference System
- Cells are referenced using Excel-style notation (A1, B2, etc.)
- Column indices convert to letters: 0=A, 1=B, 25=Z, 26=AA
- Row indices are 1-based to match Excel conventions

### Common Patterns
- **Multiple tables**: Use `el.display([(table1, (row, col)), (table2, (row, col))], sheet_styler=styler)` to display multiple ExcelFrames
- **Editable cells**: Set `frame["column"][row].is_editable = True` to make cells user-editable
- **Formatting**: Use `frame.style.fmt_currency(columns=[...]).fmt_percent(columns=[...])` for formatting
- **Cross-table dependencies**: Reference cells from other tables using `el.cell(other_frame["column"][row])` in expressions
- **Dynamic positioning**: Use `el.map(lambda idx: ...)` with index-based calculations for dynamic row positioning (e.g., centering values around a specific row)
- **Prefer lowercase**: Use `el.map()` instead of `el.Map()` for consistency

### Adding New Functions
When implementing new functions (like `max`, `min`, `if_`):

1. **Cell Expression Level** (`_cell_expr.py`):
   - Create a new class inheriting from `CellExpr`
   - Implement required methods: `dependencies`, `to_formula`, `compute`, `is_primitive`, `update_cell_refs`
   - For binary operations, follow the pattern of existing classes like `Add`, `Sub`, etc.
   - Use Excel function syntax in `to_formula()` (e.g., `"MAX({left}, {right})"`, `"IF({condition}, {true}, {false})"`)

2. **Column Expression Level** (`_expr.py`):
   - Import the new cell expression class at the top
   - Create a wrapper class inheriting from `Expr`
   - Implement `get_cell_expr()` and `_fallback_repr()` methods
   - Create a user-facing function that returns an instance of the wrapper class

3. **Export** (`__init__.py`):
   - Add imports for both the cell expression class and user function
   - Add the user function to `__all__` list

This pattern ensures the function works at both cell and column expression levels with proper Excel formula generation.

### Adding Operators to Expr Class
When implementing operators (like comparison operators):

1. **Cell Expression Level** (`_cell_expr.py`):
   - Create operator class (e.g., `Compare`) that handles the operation at cell level
   - Support multiple operators via parameter (e.g., `">", "<", ">=", "<=", "=", "<>"`)

2. **Column Expression Level** (`_expr.py`):
   - Create wrapper class (e.g., `CompareExpr`)
   - Add magic methods to `Expr` class (`__gt__`, `__lt__`, `__eq__`, etc.)
   - Handle both `Expr` and numeric literal operands by converting literals to `ConstantExpr`
   - Return instances of the wrapper class

3. **Function Naming**:
   - Use `function_name_` (with underscore) when the name conflicts with Python keywords (e.g., `if_`)

### Doctest Guidelines
- Include realistic examples that demonstrate the function's usage
- Use proper formatting that matches actual output (including column widths)
- Add empty line before closing ``` to match actual output format
- Use numeric values instead of strings for `el.lit()` in examples
- Test doctests with `pytest --doctest-modules` to ensure they pass

### Creating Examples
When creating examples in the `examples/` directory:
- Use `el.ExcelFrame.empty()` to create empty dataframes with specified columns and height
- Initialize columns with `el.lit()` for literal values or lists (e.g., `el.lit([i for i in range(10)])`)
- Reference other columns using `el.col("column_name")` for formulas and expressions
- Use `el.display()` with position tuples: `el.display([(df, (0, 0))], sheet_styler=sheet_styler)`
- Always include a `sheet_styler = el.SheetStyler()` for consistent formatting

### Styling and Display
- Use `df.style.display_horizontally()` to display tables horizontally instead of vertically
- Apply formatters like `fmt_currency()`, `fmt_percent()`, `fmt_integer()` to style columns
- Use `el.SheetStyler().cols_width()` to set column widths in the Excel output
