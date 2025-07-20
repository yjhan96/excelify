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

import { createContext, useReducer, useContext } from "react";
import type { ReactNode, ActionDispatch } from "react";
import type { Pos } from "./pos";

export interface Dimension {
  width: number;
  height: number;
}

export interface CellContent {
  formula: string;
  value: string;
  depIndices: [number, number][];
  is_editable: boolean;
  color: string;
}

export interface Sheet {
  table: CellContent[][];
  startPos: Pos;
  displayDimension: Dimension;
}

export type Sheets = Sheet[];

export interface SheetsResponse {
  tables: Sheet[];
  colStyles: object;
}

export interface SheetsState {
  sheets: Sheet[];
  colStyles: Map<number, number>;
}
export type SheetsOrError = SheetsState | { error: string };
export type SheetsAction =
  | { type: "setSheet"; sheets: SheetsResponse }
  | { type: "setError"; error: string };

const SheetsContext = createContext<SheetsOrError>({ error: "Uninitialized" });
const SheetsDispatchContext = createContext<ActionDispatch<
  [action: SheetsAction]
> | null>(null);

export function SheetsProvider({ children }: { children: ReactNode }) {
  const [sheet, dispatch] = useReducer(sheetsReducer, {
    error: "uinitialized",
  });
  return (
    <SheetsContext.Provider value={sheet}>
      <SheetsDispatchContext.Provider value={dispatch}>
        {children}
      </SheetsDispatchContext.Provider>
    </SheetsContext.Provider>
  );
}

export function useSheets() {
  return useContext(SheetsContext);
}

export function useSheetsDispatch() {
  const dispatch = useContext(SheetsDispatchContext);
  if (dispatch === null) {
    throw new Error("Sheet Dispatch must be used inside SheetProvier");
  } else {
    return dispatch;
  }
}

function sheetsReducer(_: SheetsOrError, action: SheetsAction) {
  switch (action.type) {
    case "setSheet": {
      const colStyles = new Map(
        Object.entries(action.sheets.colStyles).map(([key, value]) => [
          Number(key),
          value,
        ])
      );
      return { sheets: action.sheets.tables, colStyles: colStyles };
    }
    case "setError":
      return { error: action.error };
    default:
      throw new Error("Unknown action");
  }
}

export function isSheets(
  sheetOrError: SheetsOrError
): sheetOrError is SheetsState {
  return !("error" in sheetOrError);
}
