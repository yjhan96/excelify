import {
    ReactNode,
    createContext,
    useReducer,
    useContext,
    ActionDispatch,
} from "react";
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

function sheetsReducer(sheets: SheetsOrError, action: SheetsAction) {
    switch (action.type) {
        case "setSheet":
            const colStyles = new Map(
                Object.entries(action.sheets.colStyles).map(([key, value]) => [
                    Number(key),
                    value,
                ])
            );
            return { sheets: action.sheets.tables, colStyles: colStyles };
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
