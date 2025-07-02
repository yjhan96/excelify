import type { DialogProps } from "../types";

export function Dialog({ children, onClose }: DialogProps) {
    return (
        <div
            className="fixed inset-0 bg-gray-400/30 flex items-center justify-center z-40 p-4"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full mx-auto transform transition-all duration-300 scale-100 opacity-100"
                onClick={(e) => e.stopPropagation()}
            >
                {children}
            </div>
        </div>
    );
}
