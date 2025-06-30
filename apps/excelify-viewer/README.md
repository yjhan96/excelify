# Excelify-viewer

A web-based spreadsheet viewer that allows users to load and interact with data tables generated from excelify. Excelify bridges the gap between Python data processing and interactive spreadsheet visualization.

Click [here](https://github.com/yjhan96/excelify) to learn more about excelify.

## Features

- 📊 **Interactive Spreadsheet**: Excel-like interface with cell editing and navigation
- 🐍 **Python Integration**: Load data from Python scripts using the `excelify` library

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- npm or yarn

### Running the Application

You need to run both the frontend and backend servers:

**Terminal 1 - Frontend (React + Vite)**

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

**Terminal 2 - Backend (Flask)**

```bash
npm run start-api -- --file-path $FILENAME
```

We've included `df.py` file in the root directory of the repo as an example.

The backend API will run on `http://localhost:5000`

The frontend automatically proxies API requests to the backend.

#### Example Python Script

```python
import excelify as el

# Create a data frame
df = el.ExcelFrame.empty(columns=["year", "value"], height=10)
df = df.with_columns(
    year=el.lit([2020 + i for i in range(10)]),
    value=el.lit([100 * (i + 1) for i in range(10)])
)

# Display in Excelify
el.display([(df, (0, 0))])
```

## Available Scripts

In the project directory, you can run:

- `npm run dev` - Start Vite development server
- `npm run build` - Build for production

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Notes

For developers working on this codebase, see [CLAUDE.md](./CLAUDE.md) for detailed architecture information and development guidelines.
