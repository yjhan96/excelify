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
import type { SaveDialogProps } from "../types";
import { saveSheet } from "../services/api";
import { useParams } from "react-router";

export function SaveDialog({ setDialog, setOpen }: SaveDialogProps) {
  const [filename, setFilename] = useState<string>("spreadsheet.xlsx");
  const { "*": splat } = useParams();

  const handleSave = () => {
    saveSheet(splat, filename);
    setDialog(null);
    setOpen(false);
  };

  const handleClose = () => {
    setDialog(null);
    setOpen(false);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    switch (e.key) {
      case "Enter":
        handleSave();
        e.preventDefault();
        break;
      case "Escape":
        handleClose();
        e.preventDefault();
        break;
      default:
        break;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96 max-w-md mx-4">
        <h2 className="text-xl font-semibold mb-4">Save Spreadsheet</h2>

        <input
          type="text"
          value={filename}
          onChange={(e) => setFilename(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter filename..."
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
            onClick={handleSave}
            className="px-4 py-2 bg-cyan-600 text-white rounded hover:bg-cyan-700 transition duration-150"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
