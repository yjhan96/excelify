import type { SheetsState, Sheet } from "../sheet";
import type { Pos } from "../pos";

export function GetColAlphabet(colIdx: number): string {
    if (colIdx === 0) {
        return "A";
    }
    let res = "";
    const num_alphabets = 26;
    while (colIdx > 0) {
        const rem = colIdx % num_alphabets;
        const char = String.fromCharCode(
            "A".charCodeAt(0) + rem + (res.length === 0 ? 0 : -1)
        );
        res += char;
        colIdx = Math.floor(colIdx / num_alphabets);
    }
    return res.split("").reverse().join("");
}

export function findSheetWithCellPos(
    sheets: SheetsState,
    pos: Pos
): Sheet | undefined {
    const { row: r, col: c } = pos;
    return sheets.sheets.find((sheet) => {
        const tableStartRow = sheet.startPos.row;
        const tableStartCol = sheet.startPos.col;
        const tableEndRow = tableStartRow + sheet.displayDimension.height;
        const tableEndCol = tableStartCol + sheet.displayDimension.width;

        return (
            r >= tableStartRow &&
            r < tableEndRow &&
            c >= tableStartCol &&
            c < tableEndCol
        );
    });
}

export function cumulativeSum(array: number[]): number[] {
    let sum = 0;
    return array.map((num) => {
        const res = sum;
        sum += num;
        return res;
    });
}

export const depBorderColors = [
    "ring-green-400 border-green-400",
    "ring-sky-400 border-sky-400",
    "ring-amber-400 border-amber-400",
    "ring-pink-400 border-pink-400",
    "ring-indigo-400 border-indigo-400",
];
