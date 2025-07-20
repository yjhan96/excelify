/*
 * Copyright 2025 Albert Han
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { useState, useEffect, type RefObject, useRef } from "react";
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
