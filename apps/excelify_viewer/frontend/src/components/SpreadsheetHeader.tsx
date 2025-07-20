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

import type { SpreadsheetHeaderProps } from "../types";
import { GetColAlphabet } from "../utils";

export function SpreadsheetHeader({
    colHeaderRef,
    defaultCellWidth,
    colWidths,
    colStarts,
    visibleRange,
}: SpreadsheetHeaderProps) {
    const colsToRender = [];
    for (let c = visibleRange.startCol; c <= visibleRange.endCol; c++) {
        colsToRender.push({
            colIndex: c,
            leftPos: colStarts[c],
            width: colWidths[c],
        });
    }
    const totalWidth = colWidths.reduce((acc, curr) => acc + curr, 0);

    return (
        <div className="flex-shrink-0 flex border-b border-gray-300 shadow-sm z-10 bg-white">
            {/* Top-left fixed corner cell. */}
            <div
                style={{ width: `${defaultCellWidth + 1}px` }}
                className="h-6 flex-shrink-0 bg-gray-1000 border-r border-gray-300
            flex items-center justify-center text-sm font-semibold text-gray-500 rounded-tl-lg"
            >
                <span className="text-xs text-gray-400">Sheet</span>
            </div>

            <div
                ref={colHeaderRef}
                className="flex-grow overflow-hidden relative"
            >
                <div className="flex" style={{ width: `${totalWidth}px` }}>
                    {colsToRender.map(({ colIndex, leftPos, width }) => {
                        return (
                            <div
                                key={colIndex}
                                className="h-6 flex-shrink-0 bg-gray-100 border-r border-gray-200
                        flex items-center justify-center text-sm font-semibold text-gray-600 cursor-default
                        hover:bg-gray-200 transition duration-100 ease-in-out"
                                style={{
                                    position: "absolute",
                                    left: `${leftPos}px`,
                                    width: `${width}px`,
                                }}
                            >
                                {GetColAlphabet(colIndex)}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
