import type { SpreadsheetRowHeadersProps } from "../types";

export function SpreadsheetRowHeaders({
    rowHeaderRef,
    numRows,
    cellHeight,
    cellWidth,
}: SpreadsheetRowHeadersProps) {
    return (
        <div
            ref={rowHeaderRef}
            className="flex-shrink-0 overflow-hidden relative border-r border-gray-300 shadow-sm z-10 bg-white"
        >
            <div style={{ height: `${numRows * cellHeight}px` }}>
                {/* Render individual row header cells */}
                {Array.from({ length: numRows }, (_, rowIndex) => (
                    <div
                        key={rowIndex}
                        style={{ height: cellHeight, width: cellWidth }}
                        className="bg-gray-100 border-b border-gray-200
                                   flex items-center justify-center text-sm font-semibold text-gray-600 cursor-default
                                   hover:bg-gray-200 transition duration-100 ease-in-out"
                    >
                        {rowIndex + 1}
                    </div>
                ))}
            </div>
        </div>
    );
}
