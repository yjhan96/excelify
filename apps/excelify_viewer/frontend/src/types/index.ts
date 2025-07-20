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

import type { Dispatch, RefObject, SetStateAction } from "react";
import type { SheetsState } from "../sheet";
import type { Pos } from "../pos";

export interface VisibleRange {
    startRow: number;
    endRow: number;
    startCol: number;
    endCol: number;
}

export interface Dimension {
    width: number;
    height: number;
}

export const DIALOGTYPE = {
    LOAD: "add",
    SAVE: "save",
} as const;

export type DialogType = typeof DIALOGTYPE[keyof typeof DIALOGTYPE];

export interface DialogProps {
    children: React.ReactNode;
    onClose: () => void;
}

export interface LoadDialogProps {
    setDialog: Dispatch<SetStateAction<DialogType | null>>;
    setOpen: Dispatch<SetStateAction<boolean>>;
}

export interface SaveDialogProps {
    setDialog: Dispatch<SetStateAction<DialogType | null>>;
    setOpen: Dispatch<SetStateAction<boolean>>;
}

export interface FileMenuBarProps {
    setDialog: Dispatch<SetStateAction<DialogType | null>>;
}

export interface FormulaProps {
    sheets: SheetsState;
    selectedCell: Pos;
}

export interface SpreadsheetHeaderProps {
    colHeaderRef: RefObject<HTMLDivElement | null>;
    defaultCellWidth: number;
    colWidths: number[];
    colStarts: number[];
    visibleRange: VisibleRange;
}

export interface SpreadsheetRowHeadersProps {
    rowHeaderRef: RefObject<HTMLDivElement | null>;
    numRows: number;
    cellHeight: number;
    cellWidth: number;
}

export interface SpreadsheetGridProps {
    mainContentRef: RefObject<HTMLDivElement | null>;
    sheets: SheetsState;
    editingCell: Pos | null;
    setEditingCell: Dispatch<Pos | null>;
    numRows: number;
    colWidths: number[];
    colStarts: number[];
    cellHeight: number;
    visibleRange: VisibleRange;
    setVisibleRange: Dispatch<SetStateAction<VisibleRange>>;
    selectedCell: Pos;
    setSelectedCell: Dispatch<Pos>;
}
