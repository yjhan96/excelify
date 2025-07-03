import { useRef, useEffect, useMemo } from "react";
import { useSheetsDispatch } from "../sheet";
import { updateCellValue } from "../services/api";
import type { SpreadsheetGridProps } from "../types";
import { findSheetWithCellPos } from "../utils";
import { getCellStyles } from "../utils/cellRendering";
import type { CellRenderData } from "../utils/cellRendering";
import { useKeyboardNavigation } from "../hooks/useKeyboardNavigation";
import { useVirtualScrolling } from "../hooks/useVirtualScrolling";
import { useCellEditing } from "../hooks/useCellEditing";
import { useParams } from "react-router";

export function SpreadsheetGrid({
  mainContentRef,
  sheets,
  editingCell,
  setEditingCell,
  numRows,
  colWidths,
  colStarts,
  cellHeight,
  visibleRange,
  setVisibleRange,
  selectedCell,
  setSelectedCell,
}: SpreadsheetGridProps) {
  const dispatchSheets = useSheetsDispatch();
  const selectedCellRef = useRef<HTMLDivElement | null>(null);
  const { "*": splat } = useParams();
  const numCols = colWidths.length;

  // Custom hooks
  const {
    editingCellValue,
    setEditingCellValue,
    editingCellContent,
    expandedCellDim,
    editingCellContentRef,
  } = useCellEditing({
    editingCell,
    sheets,
    colWidths,
    cellHeight,
  });

  const handleCellUpdate = (
    value: string,
    pos: { row: number; col: number }
  ) => {
    updateCellValue(dispatchSheets, splat, value, pos);
  };

  const { handleKeyDown } = useKeyboardNavigation({
    selectedCell,
    setSelectedCell,
    editingCell,
    setEditingCell,
    numRows,
    numCols,
    editingCellValue,
    onCellUpdate: handleCellUpdate,
    visibleRange,
    mainContentRef,
    colStarts,
    cellHeight,
    setVisibleRange,
  });

  useVirtualScrolling({
    mainContentRef,
    numRows,
    numCols,
    cellHeight,
    colStarts,
    setVisibleRange,
  });

  // Auto-scroll to selected cell
  useEffect(() => {
    if (selectedCellRef.current) {
      selectedCellRef.current.scrollIntoView({
        behavior: "auto",
        block: "nearest",
        inline: "nearest",
      });
    }
  }, [selectedCell]);

  // Set up keyboard event listeners
  useEffect(() => {
    const gridElement = mainContentRef.current;
    if (gridElement) {
      if (editingCell === null) {
        gridElement.focus();
      }
      gridElement.addEventListener("keydown", handleKeyDown);
      return () => {
        gridElement.removeEventListener("keydown", handleKeyDown);
      };
    }
  }, [handleKeyDown, mainContentRef, editingCell]);

  // Generate cells to render (memoized for performance)
  const cellsToRender = useMemo((): CellRenderData[] => {
    const cells: CellRenderData[] = [];
    for (let r = visibleRange.startRow; r <= visibleRange.endRow; r++) {
      for (let c = visibleRange.startCol; c <= visibleRange.endCol; c++) {
        const sheet = findSheetWithCellPos(sheets, { row: r, col: c });
        if (sheet === undefined) {
          cells.push({
            row: r,
            col: c,
            value: "",
            isEditable: false,
            valueColor: "black",
          });
        } else {
          const rowIndex = r - sheet.startPos.row;
          const colIndex = c - sheet.startPos.col;
          const isEditing = editingCell?.row === r && editingCell?.col === c;
          const cell = sheet.table[colIndex][rowIndex];
          cells.push({
            row: r,
            col: c,
            value: isEditing ? cell.formula : cell.value,
            isEditable: cell.is_editable,
            valueColor: cell.color,
          });
        }
      }
    }
    return cells;
  }, [visibleRange, sheets, editingCell]);

  const totalWidth = colWidths.reduce((acc, curr) => acc + curr, 0);

  return (
    <div
      ref={mainContentRef}
      className="flex-grow overflow-auto bg-white rounded-br-lg focus:outline-none"
      tabIndex={0}
    >
      <div
        style={{
          width: `${totalWidth}px`,
          height: `${numRows * cellHeight}px`,
        }}
        className="relative"
      >
        {cellsToRender.map(({ row, col, value, isEditable, valueColor }) => {
          const isEditing =
            editingCell?.row === row && editingCell?.col === col;
          const isSelected =
            selectedCell.row === row && selectedCell.col === col;

          const { cellStyle, borderColor } = getCellStyles(
            row,
            col,
            isEditing,
            isSelected,
            isEditable,
            editingCell,
            editingCellContent
          );

          const contentDiv =
            isEditable && isEditing ? (
              <>
                <input
                  type="text"
                  value={editingCellValue}
                  onChange={(e) => setEditingCellValue(e.target.value)}
                  onBlur={() => setEditingCell(null)}
                  autoFocus
                  className="w-full h-full border-none focus:outline-none bg-transparent rounded-sm text-sm p-1"
                />
                <div className="invisible fixed" ref={editingCellContentRef}>
                  {editingCellValue}
                </div>
              </>
            ) : (
              <div
                className="flex items-center justify-start whitespace-nowrap overflow-hidden text-ellipsis cursor-text"
                ref={isEditing ? editingCellContentRef : undefined}
                style={{
                  color: valueColor,
                }}
              >
                {value}
              </div>
            );

          return (
            <div
              key={`${row}-${col}`}
              className={`table-cell ${cellStyle} ${borderColor}`}
              style={{
                position: "absolute",
                left: `${colStarts[col]}px`,
                top: `${row * cellHeight}px`,
                height: `${isEditing ? expandedCellDim?.height : cellHeight}px`,
                width: `${
                  isEditing ? expandedCellDim?.width : colWidths[col]
                }px`,
              }}
              ref={isSelected ? selectedCellRef : undefined}
              onClick={() => {
                setSelectedCell({ row, col });
                setEditingCell(null);
              }}
            >
              {contentDiv}
            </div>
          );
        })}
      </div>
    </div>
  );
}
