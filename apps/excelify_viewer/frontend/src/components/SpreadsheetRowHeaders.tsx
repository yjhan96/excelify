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
