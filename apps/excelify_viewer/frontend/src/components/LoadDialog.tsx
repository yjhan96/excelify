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

import { useState, type KeyboardEvent } from "react";
import { useSheetsDispatch } from "../sheet";
import type { LoadDialogProps } from "../types";
import { useNavigate } from "react-router";

export function LoadDialog({ setDialog, setOpen }: LoadDialogProps) {
  const dispatchSheets = useSheetsDispatch();
  const navigate = useNavigate();
  const [inputValue, setInputValue] = useState("");

  function loadFile() {
    dispatchSheets({ type: "setError", error: "Reloading..." });
    setOpen(false);
    setDialog(null);
    navigate(`/sheet/${inputValue}`);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    switch (e.key) {
      case "Enter":
        loadFile();
        e.preventDefault();
        break;
      case "Escape":
        handleClose();
        e.preventDefault();
        break;
      default:
        break;
    }
  }

  const handleClose = () => {
    setDialog(null);
    setOpen(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96 max-w-md mx-4">
        <h2 className="text-xl font-semibold mb-4">Load Python Script</h2>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter the file path..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent mb-4"
          autoFocus
        />

        <div className="flex justify-end space-x-3">
          <button
            onClick={handleClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition duration-150"
          >
            Cancel
          </button>
          <button
            onClick={loadFile}
            className="px-4 py-2 bg-cyan-600 text-white rounded hover:bg-cyan-700 transition duration-150"
          >
            Load
          </button>
        </div>
      </div>
    </div>
  );
}
