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
