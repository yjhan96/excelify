import type { FormulaProps } from "../types";
import { findSheetWithCellPos } from "../utils";

export function Formula({ sheets, selectedCell }: FormulaProps) {
    const sheet = findSheetWithCellPos(sheets, selectedCell);
    let formula;
    if (sheet) {
        formula = `f(x)=${sheet.table[selectedCell.col - sheet.startPos.col][selectedCell.row - sheet.startPos.row].formula}`;
    } else {
        formula = "f(x)";
    }
    return (
        <div className="h-8 flex-shrink-0 flex border-b border-gray-300 shadow-sm z-10 bg-white">
            {formula}
        </div>
    );
}
