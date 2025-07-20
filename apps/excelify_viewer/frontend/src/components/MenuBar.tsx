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

import { useState, useRef, useEffect } from "react";
import { useSheetsDispatch } from "../sheet";
import { reloadSheet } from "../services/api";
import { DIALOGTYPE, type DialogType } from "../types";
import { FileMenuBar } from "./FileMenuBar";
import { LoadDialog } from "./LoadDialog";
import { SaveDialog } from "./SaveDialog";
import imgUrl from "../assets/images/koala.svg";
import { useParams } from "react-router";

export function MenuBar() {
  const dispatchSheets = useSheetsDispatch();
  const [open, setOpen] = useState(false);
  const [dialog, setDialog] = useState<DialogType | null>(null);
  const dropdownRef = useRef<HTMLLIElement | null>(null);
  const { "*": splat } = useParams();

  useEffect(() => {
    function close(e: MouseEvent) {
      const current = dropdownRef.current;
      if (
        !current ||
        (e.target instanceof Node && !current.contains(e.target))
      ) {
        setOpen(false);
      }
    }

    if (open) {
      window.addEventListener("click", close);
    }
    return () => {
      window.removeEventListener("click", close);
    };
  }, [open]);

  const dialogContent =
    dialog === DIALOGTYPE.LOAD ? (
      <LoadDialog setDialog={setDialog} setOpen={setOpen} />
    ) : dialog === DIALOGTYPE.SAVE ? (
      <SaveDialog setDialog={setDialog} setOpen={setOpen} />
    ) : (
      <></>
    );

  return (
    <>
      <div className="flex-shrink-0 bg-stone-200 text-gray-800 shadow-md z-30">
        <nav className="flex items-center px-4 py-2">
          <img className="w-6 h-7 mr-2 ml-0" src={imgUrl} alt="Koala" />
          <div className="font-semibold text-lg mr-6">Excelify</div>
          <ul className="flex space-x-6 text-sm">
            <li className="relative" ref={dropdownRef}>
              <button
                className="hover:text-gray-300 transition duration-150 ease-in-out cursor-pointer"
                onClick={() => setOpen(!open)}
              >
                File
              </button>
              {open && <FileMenuBar setDialog={setDialog} />}
            </li>
            <li>
              <button
                className="hover:text-gray-300 transition duration-150 ease-in-out cursor-pointer"
                onClick={() => {
                  reloadSheet(dispatchSheets, splat);
                }}
              >
                Reload
              </button>
            </li>
          </ul>
        </nav>
      </div>
      {dialogContent}
    </>
  );
}
