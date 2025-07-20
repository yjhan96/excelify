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

import type { FileMenuBarProps } from "../types";
import { DIALOGTYPE } from "../types";

export function FileMenuBar({ setDialog }: FileMenuBarProps) {
  return (
    <div className="absolute top-full left-0 mt-2 w-40 bg-white text-gray-800 rounded-md shadow-lg py-1 z-40">
      <button
        className="block px-4 py-2 hover:bg-gray-100 w-full text-start cursor-pointer"
        onClick={() => setDialog(DIALOGTYPE.LOAD)}
      >
        Load
      </button>
      <button
        className="block px-4 py-2 hover:bg-gray-100 w-full text-start cursor-pointer"
        onClick={() => setDialog(DIALOGTYPE.SAVE)}
      >
        Save
      </button>
    </div>
  );
}
