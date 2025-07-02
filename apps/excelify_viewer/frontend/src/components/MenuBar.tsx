import { useState, useRef, useEffect } from "react";
import { useSheetsDispatch } from "../sheet";
import { reloadSheet } from "../services/api";
import { DIALOGTYPE, type DialogType } from "../types";
import { FileMenuBar } from "./FileMenuBar";
import { LoadDialog } from "./LoadDialog";
import { SaveDialog } from "./SaveDialog";
import imgUrl from "../assets/images/koala.svg";

export function MenuBar() {
  const dispatchSheets = useSheetsDispatch();
  const [open, setOpen] = useState(false);
  const [dialog, setDialog] = useState<DialogType | null>(null);
  const dropdownRef = useRef<HTMLLIElement | null>(null);

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
                  reloadSheet(dispatchSheets);
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
