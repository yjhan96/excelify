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

import type { CellContent } from "../sheet";
import type { Pos } from "../pos";
import { depBorderColors } from "./index";

export interface CellRenderData {
    row: number;
    col: number;
    value: string;
    isEditable: boolean;
    valueColor: string;
}

export function getCellStyles(
    row: number,
    col: number,
    isEditing: boolean,
    isSelected: boolean,
    isEditable: boolean,
    editingCell: Pos | null,
    editingCellContent: CellContent | null
) {
    // Calculate dependency index for highlighting
    let depIndex: number | null = null;
    if (editingCellContent !== null) {
        const depIndices = editingCellContent.depIndices;
        const idx = depIndices.findIndex(([depRow, depCol]) => {
            return depRow === row && depCol === col;
        });
        depIndex = idx >= 0 ? idx : null;
    }

    // Determine cell style
    let cellStyle: string;
    if (isEditing) {
        cellStyle = "editing-cell";
    } else if (isSelected) {
        cellStyle = "selected-cell";
    } else {
        if (isEditable) {
            if (editingCell && depIndex !== null) {
                cellStyle = "default-editable-cell dep-cell";
            } else {
                cellStyle = "default-editable-cell";
            }
        } else if (editingCell && depIndex !== null) {
            cellStyle = "dep-cell";
        } else {
            cellStyle = "default-cell";
        }
    }

    // Determine border color
    let borderColor: string;
    if (editingCell && depIndex !== null) {
        borderColor = depBorderColors[depIndex % depBorderColors.length];
    } else {
        borderColor = "border-gray-200";
    }

    return { cellStyle, borderColor };
}
