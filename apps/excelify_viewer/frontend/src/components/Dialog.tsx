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
