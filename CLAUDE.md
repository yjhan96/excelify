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
