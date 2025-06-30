import { useState, type KeyboardEvent } from "react";
import type { SaveDialogProps } from "../types";
import { saveSheet } from "../services/api";

export function SaveDialog({ setDialog, setOpen }: SaveDialogProps) {
    const [filename, setFilename] = useState<string>("spreadsheet.xlsx");

    const handleSave = () => {
        saveSheet(filename);
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
