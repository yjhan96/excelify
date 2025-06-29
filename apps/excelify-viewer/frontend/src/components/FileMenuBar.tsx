import type { FileMenuBarProps, DialogType } from "../types";

export function FileMenuBar({ setDialog }: FileMenuBarProps) {
    return (
        <div className="absolute top-full left-0 mt-2 w-40 bg-white text-gray-800 rounded-md shadow-lg py-1 z-40">
            <button
                className="block px-4 py-2 hover:bg-gray-100 w-full text-start cursor-pointer"
                onClick={() => setDialog(DialogType.Load)}
            >
                Load
            </button>
            <button
                className="block px-4 py-2 hover:bg-gray-100 w-full text-start cursor-pointer"
                onClick={() => setDialog(DialogType.Save)}
            >
                Save
            </button>
        </div>
    );
}
