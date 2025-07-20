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
