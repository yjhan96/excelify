import "./App.css";
import { useState, useRef, useEffect } from "react";
import {
  useSheets,
  isSheets,
  SheetsProvider,
  useSheetsDispatch,
} from "./sheet";
import { UserStateProvider } from "./userState";
import type { Pos } from "./pos";
import { getSheet } from "./services/api";
import { cumulativeSum } from "./utils";
import { MenuBar } from "./components/MenuBar";
import { Formula } from "./components/Formula";
import { SpreadsheetHeader } from "./components/SpreadsheetHeader";
import { SpreadsheetRowHeaders } from "./components/SpreadsheetRowHeaders";
import { SpreadsheetGrid } from "./components/SpreadsheetGrid";
import { useParams } from "react-router";

function AppInternal() {
  const numRows = 100;
  const numCols = 50;
  const defaultCellHeight = 20;
  const defaultCellWidth = 64;

  const sheets = useSheets();
  const dispatchSheets = useSheetsDispatch();
  const { "*": splat } = useParams();

  const [editingCell, setEditingCell] = useState<Pos | null>(null);
  const [selectedCell, setSelectedCell] = useState<Pos>({ row: 0, col: 0 });
  const [visibleRange, setVisibleRange] = useState({
    startRow: 0,
    endRow: Math.min(numRows - 1, 20),
    startCol: 0,
    endCol: Math.min(numCols - 1, 20),
  });

  const mainContentRef = useRef<HTMLDivElement | null>(null);
  const colHeaderRef = useRef<HTMLDivElement | null>(null);
  const rowHeaderRef = useRef<HTMLDivElement | null>(null);

  // Synchronize scroll between headers and main content
  useEffect(() => {
    const mainContentElement = mainContentRef.current;
    if (mainContentElement) {
      const handleScroll = () => {
        if (colHeaderRef.current) {
          colHeaderRef.current.scrollLeft = mainContentElement.scrollLeft;
        }
        if (rowHeaderRef.current) {
          rowHeaderRef.current.scrollTop = mainContentElement.scrollTop;
        }
      };
      mainContentElement.addEventListener("scroll", handleScroll);
      return () =>
        mainContentElement.removeEventListener("scroll", handleScroll);
    }
  }, [sheets]);

  // Load initial sheet data
  useEffect(() => {
    getSheet(dispatchSheets, splat);
  }, [dispatchSheets, splat]);

  let content;
  if (isSheets(sheets)) {
    const colWidths = Array.from({ length: numCols }, (_, colIndex) => {
      return sheets.colStyles.get(colIndex) ?? defaultCellWidth;
    });
    const colStarts = cumulativeSum(colWidths);

    content = (
      <>
        <Formula sheets={sheets} selectedCell={selectedCell} />
        <SpreadsheetHeader
          colHeaderRef={colHeaderRef}
          defaultCellWidth={defaultCellWidth}
          colWidths={colWidths}
          colStarts={colStarts}
          visibleRange={visibleRange}
        />
        <div className="flex flex-grow overflow-hidden">
          <SpreadsheetRowHeaders
            rowHeaderRef={rowHeaderRef}
            numRows={numRows}
            cellHeight={defaultCellHeight}
            cellWidth={defaultCellWidth}
          />
          <SpreadsheetGrid
            mainContentRef={mainContentRef}
            sheets={sheets}
            editingCell={editingCell}
            setEditingCell={setEditingCell}
            numRows={numRows}
            colWidths={colWidths}
            colStarts={colStarts}
            cellHeight={defaultCellHeight}
            visibleRange={visibleRange}
            setVisibleRange={setVisibleRange}
            selectedCell={selectedCell}
            setSelectedCell={setSelectedCell}
          />
        </div>
      </>
    );
  } else {
    content = (
      <div className="flex flex-grow overflow-hidden">
        Reloading the table...
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen font-inter bg-gray-50 text-gray-800">
      <MenuBar />
      {content}
    </div>
  );
}

export default function App() {
  return (
    <SheetsProvider>
      <UserStateProvider>
        <AppInternal />
      </UserStateProvider>
    </SheetsProvider>
  );
}
