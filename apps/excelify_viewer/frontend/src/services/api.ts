import type { Dispatch } from "react";
import type { SheetsAction, SheetsResponse } from "../sheet";
import type { Pos } from "../pos";

export function reloadSheet(dispatchSheets: Dispatch<SheetsAction>, scriptPath: string | undefined): void {
    dispatchSheets({ type: "setError", error: "Reloading..." });
    fetch("/api/reload", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            body: JSON.stringify({}),
        },
        body: JSON.stringify({
            scriptPath: scriptPath,
        })
    })
        .then((res) => res.json())
        .then((data: SheetsResponse) => {
            dispatchSheets({ type: "setSheet", sheets: data });
        })
        .catch((error) => {
            console.log("received error" + error);
        });
}

export function loadSheet(path: string, dispatchSheets: Dispatch<SheetsAction>): void {
    fetch("/api/load", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            path: path,
        }),
    })
        .then((res) => res.json())
        .then((data: SheetsResponse) => {
            dispatchSheets({
                type: "setSheet",
                sheets: data,
            });
        })
        .catch((error) => {
            console.log("received error" + error);
        });
}

export function updateCellValue(
    dispatchSheets: Dispatch<SheetsAction>,
    scriptPath: string | undefined,
    updatedValue: string,
    pos: Pos,
): void {
    fetch("/api/update", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            scriptPath: scriptPath,
            value: updatedValue,
            pos: [pos.row, pos.col],
        }),
    })
        .then((res) => res.json())
        .then((data: SheetsResponse) => {
            dispatchSheets({
                type: "setSheet",
                sheets: data,
            });
        })
        .catch((error) => {
            console.log("Received error" + error);
        });
}

export function getSheet(dispatchSheets: Dispatch<SheetsAction>, scriptPath: string | undefined): void {
    fetch(`/api/sheet?scriptPath=${scriptPath}`)
        .then((res) => res.json())
        .then((sheets: SheetsResponse) => {
            dispatchSheets({ type: "setSheet", sheets: sheets });
        })
        .catch((error) => {
            dispatchSheets({ type: "setError", error: error });
        });
}

export function saveSheet(scriptPath: string | undefined, filename: string) {
    fetch("/api/save", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            scriptPath: scriptPath,
            filename: filename,
        }),
    })
        .catch((error) => {
            console.log("received error" + error);
        })
}
