# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the frontend React application for Excelify Viewer, a web-based spreadsheet viewer that displays Excel-like spreadsheets created by the Excelify Python library. The application provides an interactive spreadsheet interface with formula editing, cell navigation, and data visualization capabilities.

### Core Architecture

The application follows a typical React pattern with several key architectural components:

- **State Management**: Uses React Context API with `SheetsProvider` and `SheetsDispatchContext` for managing spreadsheet data globally
- **Component Structure**: Modular components for different parts of the spreadsheet interface (grid, headers, formula bar, menus)
- **Virtual Scrolling**: Custom virtualization for handling large spreadsheets efficiently without rendering all cells
- **API Communication**: RESTful API calls to a Python backend server running on port 5000
- **Cell System**: Each cell contains formula, value, dependencies, and styling information

### Key Components

- **App.tsx**: Main application container with layout and state initialization
- **SpreadsheetGrid**: Core spreadsheet rendering component with virtual scrolling
- **Formula**: Formula bar component for displaying and editing cell formulas
- **SpreadsheetHeader/SpreadsheetRowHeaders**: Column and row header components
- **MenuBar/FileMenuBar**: Application menu system for file operations

### State Management Pattern

The application uses a reducer pattern for managing spreadsheet state:
- `SheetsState`: Contains spreadsheet data and column styling information
- `SheetsAction`: Actions for updating state (setSheet, setError)
- API calls dispatch actions to update the global state

### Custom Hooks

- **useVirtualScrolling**: Manages visible cell range for performance optimization
- **useCellEditing**: Handles cell editing state and expanded cell dimensions
- **useKeyboardNavigation**: Manages keyboard navigation between cells

## Development Commands

### Development Server
```bash
npm run dev
```
Starts Vite development server with hot module replacement. The backend API is proxied from localhost:5000.

### Build
```bash
npm run build
```
Runs TypeScript compilation followed by Vite build for production.

### Linting
```bash
npm run lint
```
Runs ESLint on the codebase for code quality checks.

### Preview Build
```bash
npm run preview
```
Serves the production build locally for testing.

## API Integration

The frontend communicates with a Python Flask backend via REST API:
- `/api/sheet` - GET current spreadsheet data
- `/api/load` - POST to load a new spreadsheet file
- `/api/save` - POST to save current spreadsheet
- `/api/update` - PUT to update cell values
- `/api/reload` - PUT to reload current spreadsheet

All API calls are handled through the `services/api.ts` module and follow a consistent pattern of dispatching actions to update global state.

## Virtual Scrolling Implementation

The application implements custom virtual scrolling to handle large spreadsheets:
- Only renders visible cells plus a buffer zone
- Dynamically calculates visible range based on scroll position
- Maintains synchronized scrolling between headers and main grid
- Uses `colStarts` array for efficient column position calculations

## Cell Reference System

Follows Excel-style cell referencing:
- Positions are tracked as `{row: number, col: number}` objects
- Column indices map to Excel letters (0=A, 1=B, etc.)
- Row indices are 0-based internally but displayed as 1-based to users
- Cells contain dependency information for formula evaluation
