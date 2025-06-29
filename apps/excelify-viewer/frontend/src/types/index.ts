import { Dispatch, RefObject, SetStateAction } from "react";
import type {  SheetsState } from "../sheet";
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

export enum DialogType {
    Load,
    Save,
}

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
