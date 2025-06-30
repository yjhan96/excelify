import type { Dispatch, RefObject } from "react";
import type { Dimension } from "../types";
import type { Pos } from "../pos";

export function updateExpandedCellDim(
    editingCell: Pos | null,
    editingCellContentRef: RefObject<HTMLDivElement | null>,
    setExpandedCellDim: Dispatch<Dimension>,
    cellWidths: number[],
    cellHeight: number,
) {
    if (editingCell && editingCellContentRef.current) {
        const contentDiv = editingCellContentRef.current;
        const contentWidth = contentDiv.scrollWidth;
        const margin = 15;

        let width = cellWidths[editingCell.col];
        let currColIndex = editingCell.col;
        while (
            contentWidth + margin > width &&
            currColIndex < cellWidths.length - 1
        ) {
            currColIndex += 1;
            width += cellWidths[currColIndex];
        }

        setExpandedCellDim({
            width: width,
            height: cellHeight,
        });
    }
}
