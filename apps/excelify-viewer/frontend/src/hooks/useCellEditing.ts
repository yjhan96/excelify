import { useState, useEffect, RefObject, useRef } from "react";
import type { Pos } from "../pos";
import type { SheetsState, CellContent } from "../sheet";
import type { Dimension } from "../types";
import { findSheetWithCellPos } from "../utils";
import { updateExpandedCellDim } from "../utils/spreadsheetHelpers";

interface UseCellEditingProps {
    editingCell: Pos | null;
    sheets: SheetsState;
    colWidths: number[];
    cellHeight: number;
}

export function useCellEditing({
    editingCell,
    sheets,
    colWidths,
    cellHeight,
}: UseCellEditingProps) {
    const [editingCellValue, setEditingCellValue] = useState<string>("");
    const [editingCellContent, setEditingCellContent] = useState<CellContent | null>(null);
    const [expandedCellDim, setExpandedCellDim] = useState<Dimension | null>(null);
    const editingCellContentRef: RefObject<HTMLDivElement | null> = useRef(null);
    // Update editing cell content when editingCell or sheets change
    useEffect(() => {
        if (editingCell) {
            const sheet = findSheetWithCellPos(sheets, editingCell);
            if (sheet !== undefined) {
                const rowIndex = editingCell.row - sheet.startPos.row;
                const colIndex = editingCell.col - sheet.startPos.col;
                const cell = sheet.table[colIndex][rowIndex];
                setEditingCellContent(cell);
                setEditingCellValue(cell.formula);
            } else {
                setEditingCellContent(null);
                setEditingCellValue("");
            }
        } else {
            setEditingCellContent(null);
            setEditingCellValue("");
        }
    }, [editingCell, sheets]);

    // Update expanded cell dimensions when editing
    useEffect(() => {
        updateExpandedCellDim(
            editingCell,
            editingCellContentRef,
            setExpandedCellDim,
            colWidths,
            cellHeight,
        );
    }, [editingCell, colWidths, cellHeight, editingCellContentRef, editingCellValue]);

    return {
        editingCellValue,
        setEditingCellValue,
        editingCellContent,
        expandedCellDim,
        editingCellContentRef,
    };
}
