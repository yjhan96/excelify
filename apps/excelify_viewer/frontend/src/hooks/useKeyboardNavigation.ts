import { useCallback, type RefObject } from "react";
import type { Pos } from "../pos";
import type { VisibleRange } from "../types";

function maybeUpdateVisibleRange(
    mainContentRef: RefObject<HTMLDivElement | null>,
    selectedCell: Pos,
    visibleRange: VisibleRange,
    numRows: number,
    numCols: number,
    colStarts: number[],
    cellHeight: number,
    setVisibleRange: (updater: (prev: VisibleRange) => VisibleRange) => void,
) {
    if (mainContentRef.current) {
            const {clientHeight, clientWidth} = mainContentRef.current;
            const rowBuffer = 5;
            const colBuffer = 3;
            let startRow: number, endRow: number, startCol: number, endCol: number;
            if (selectedCell.row < visibleRange.startRow) {
                startRow = Math.max(0, selectedCell.row - rowBuffer);
                endRow = Math.min(
                    numRows - 1,
                    Math.ceil(startRow + (clientHeight / cellHeight) + rowBuffer),
                );
            } else if (selectedCell.row >= visibleRange.endRow) {
                endRow = Math.min(selectedCell.row + rowBuffer, numRows - 1);
                startRow = Math.max(
                    0,
                    Math.floor(endRow - (clientHeight / cellHeight) - rowBuffer),
                );
            } else {
                startRow = visibleRange.startRow;
                endRow = visibleRange.endRow;
            }

            if (selectedCell.col < visibleRange.startCol) {
                startCol = Math.max(0, selectedCell.col - colBuffer);
                endCol = Math.min(
                    numCols - 1,
                    colStarts.findLastIndex(
                        (colStart: number) => colStarts[startCol] + clientWidth >= colStart,
                    ) + colBuffer,
                );
            } else if (selectedCell.col >= visibleRange.endCol) {
                endCol = Math.min(selectedCell.col + colBuffer, numCols - 1);
                startCol = Math.max(
                    0,
                    colStarts.findIndex(
                        (colStart: number) => colStarts[endCol] - clientWidth < colStart
                    ) - colBuffer,
                );
            } else {
                startCol = visibleRange.startCol;
                endCol = visibleRange.endCol;
            }

            setVisibleRange((prevState: VisibleRange) => {
                if (
                    prevState.startRow === startRow &&
                    prevState.startCol === startCol &&
                    prevState.endRow === endRow &&
                    prevState.endCol === endCol
                ) {
                    return prevState;
                } else {
                    return {startRow, endRow, startCol, endCol};
                }
            });
    }
}

interface UseKeyboardNavigationProps {
    selectedCell: Pos;
    setSelectedCell: (pos: Pos) => void;
    editingCell: Pos | null;
    setEditingCell: (pos: Pos | null) => void;
    numRows: number;
    numCols: number;
    editingCellValue: string;
    onCellUpdate: (value: string, pos: Pos) => void;
    visibleRange: VisibleRange,
    mainContentRef: RefObject<HTMLDivElement | null>,
    colStarts: number[],
    cellHeight: number,
    setVisibleRange: (updater: (prev: VisibleRange) => VisibleRange) => void,
}

export function useKeyboardNavigation({
    selectedCell,
    setSelectedCell,
    editingCell,
    setEditingCell,
    numRows,
    numCols,
    editingCellValue,
    onCellUpdate,
    visibleRange,
    mainContentRef,
    colStarts,
    cellHeight,
    setVisibleRange
}: UseKeyboardNavigationProps) {
    const handleKeyDown = useCallback(
        (e: globalThis.KeyboardEvent) => {
            // Handle input field events when editing
            if (
                editingCell &&
                e.target instanceof Element &&
                e.target.tagName === "INPUT"
            ) {
                if (e.key === "Enter" || e.key === "Escape") {
                    onCellUpdate(editingCellValue, editingCell);
                    setEditingCell(null);
                    e.preventDefault();
                }
                return;
            }

            let newRow = selectedCell.row;
            let newCol = selectedCell.col;
            let preventDefault = true;

            switch (e.key) {
                case "ArrowUp":
                    newRow = Math.max(0, newRow - 1);
                    break;
                case "ArrowDown":
                    newRow = Math.min(numRows - 1, newRow + 1);
                    break;
                case "ArrowLeft":
                    newCol = Math.max(0, newCol - 1);
                    break;
                case "ArrowRight":
                    newCol = Math.min(numCols - 1, newCol + 1);
                    break;
                case "Enter":
                    // Enter edit mode for the selected cell
                    setEditingCell({
                        row: selectedCell.row,
                        col: selectedCell.col,
                    });
                    break;
                case "Tab":
                    if (e.shiftKey) {
                        // Shift + Tab: move left
                        if (newCol > 0) {
                            newCol--;
                        } else if (newRow > 0) {
                            newRow--;
                            newCol = numCols - 1; // Wrap to end of previous row
                        } else {
                            preventDefault = false; // Allow browser default if at top-left
                        }
                    } else {
                        // Tab: move right
                        if (newCol < numCols - 1) {
                            newCol++;
                        } else if (newRow < numRows - 1) {
                            newRow++;
                            newCol = 0; // Wrap to beginning of next row
                        } else {
                            preventDefault = false; // Allow browser default if at bottom-right
                        }
                    }
                    break;
                case "Escape":
                    // Exit editing mode if active
                    if (editingCell) {
                        setEditingCell(null);
                    } else {
                        preventDefault = false;
                    }
                    break;
                default:
                    preventDefault = false; // Don't prevent default for other keys
            }

            if (preventDefault) {
                e.preventDefault();
            }

            // Only update selected cell if it has changed and we're not in edit mode
            if (
                !editingCell &&
                (newRow !== selectedCell.row || newCol !== selectedCell.col)
            ) {
                setSelectedCell({ row: newRow, col: newCol });
                maybeUpdateVisibleRange(mainContentRef, selectedCell, visibleRange, numRows, numCols, colStarts, cellHeight, setVisibleRange);
            }
        },
        [selectedCell, editingCell, numRows, numCols, editingCellValue, onCellUpdate, setSelectedCell, setEditingCell, cellHeight, colStarts, mainContentRef, setVisibleRange, visibleRange],
    );

    return { handleKeyDown };
}
