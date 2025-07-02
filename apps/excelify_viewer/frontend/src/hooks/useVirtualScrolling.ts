import { useEffect, type RefObject } from "react";
import type { VisibleRange } from "../types";

interface UseVirtualScrollingProps {
    mainContentRef: RefObject<HTMLDivElement | null>;
    numRows: number;
    numCols: number;
    cellHeight: number;
    colStarts: number[];
    setVisibleRange: (updater: (prev: VisibleRange) => VisibleRange) => void;
}

export function useVirtualScrolling({
    mainContentRef,
    numRows,
    numCols,
    cellHeight,
    colStarts,
    setVisibleRange,
}: UseVirtualScrollingProps) {
    useEffect(() => {
        const gridElement = mainContentRef.current;
        if (!gridElement) return;

        const updateVisibleRange = () => {
            const { scrollTop, scrollLeft, clientHeight, clientWidth } = gridElement;

            const rowBuffer = 5;
            const colBuffer = 3;

            const startRow = Math.max(
                0,
                Math.floor(scrollTop / cellHeight) - rowBuffer,
            );
            const endRow = Math.min(
                numRows - 1,
                Math.ceil((scrollTop + clientHeight) / cellHeight) + rowBuffer,
            );

            const startCol = Math.max(
                0,
                colStarts.findIndex((colStart) => scrollLeft < colStart) - colBuffer,
            );
            const endCol = Math.min(
                numCols - 1,
                colStarts.findLastIndex(
                    (colStart: number) => scrollLeft + clientWidth >= colStart,
                ) + colBuffer,
            );

            setVisibleRange((prevState) => {
                if (
                    prevState.startRow === startRow &&
                    prevState.startCol === startCol &&
                    prevState.endRow === endRow &&
                    prevState.endCol === endCol
                ) {
                    return prevState;
                } else {
                    return { startRow, endRow, startCol, endCol };
                }
            });
        };

        updateVisibleRange();
        gridElement.addEventListener("scroll", updateVisibleRange);
        window.addEventListener("resize", updateVisibleRange);

        return () => {
            gridElement.removeEventListener("scroll", updateVisibleRange);
            window.removeEventListener("resize", updateVisibleRange);
        };
    }, [mainContentRef, numRows, numCols, cellHeight, colStarts, setVisibleRange]);
}
