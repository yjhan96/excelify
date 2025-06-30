import pickle
import subprocess
import sys
from pathlib import Path

from flask import Flask, make_response, request, send_from_directory
from flask_cors import CORS

import excelify as el

DATA_FILE = ".excelify-data/data.pickle"


def create_app(file_path: str, cwd_str: str):
    cwd = Path(cwd_str)
    app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
    app.config["DEBUG"] = True
    CORS(app)

    @app.route("/")
    def serve_react_app():
        assert app.static_folder is not None
        return send_from_directory(app.static_folder, "index.html")

    @app.put("/api/reload")
    def reset():
        data_path = cwd / DATA_FILE
        if data_path.exists():
            data_path.unlink()

        # TODO: Handle if the cookie doesn't exist.
        script_path = request.cookies.get("script_path")
        assert script_path is not None

        subprocess.run([sys.executable, script_path], cwd=str(cwd))

        with data_path.open("rb") as f:
            display_data: el.DisplayData = pickle.load(f)
        dfs_json = el.to_json(
            display_data.dfs,
            include_header=True,
            sheet_styler=display_data.sheet_styler,
        )
        return dfs_json

    @app.route("/api/sheet")
    def get_sheet():
        data_path = cwd / DATA_FILE
        script_path: str | None = None
        display_data: el.DisplayData
        if data_path.exists():
            with data_path.open("rb") as f:
                display_data = pickle.load(f)
        else:
            script_path = request.cookies.get("script_path")
            if script_path is None:
                print(
                    "Couldn't find cookie from the request. using default path instead."
                )
                script_path = str(file_path)
            subprocess.run([sys.executable, str(script_path)], cwd=str(cwd))
            with data_path.open("rb") as f:
                display_data = pickle.load(f)
        if not data_path.exists():
            with (cwd / DATA_FILE).open("wb") as f:
                pickle.dump(display_data, f)

        dfs_json = el.to_json(
            display_data.dfs,
            include_header=True,
            sheet_styler=display_data.sheet_styler,
        )
        resp = make_response(dfs_json)
        if script_path is not None:
            resp.set_cookie("script_path", script_path)
        return resp

    # TODO: Move this to excelify library.
    def _get_rel_pos(
        pos: tuple[int, int], df: el.ExcelFrame, start_pos: tuple[int, int]
    ) -> tuple[int, int]:
        (row_idx, col_idx) = pos
        (start_row_idx, start_col_idx) = start_pos

        match df.style.display_axis:
            case el.DisplayAxis.VERTICAL:
                rel_row_idx = row_idx - start_row_idx - 1
                rel_col_idx = col_idx - start_col_idx
                return (rel_row_idx, rel_col_idx)
            case el.DisplayAxis.HORIZONTAL:
                rel_row_idx = row_idx - start_row_idx
                rel_col_idx = col_idx - start_col_idx - 1
                return (rel_col_idx, rel_row_idx)
            case other:
                raise ValueError(f"Unknown display: {other}")

    @app.put("/api/update")
    def update_cell():
        update_data = request.get_json()
        data_path = cwd / DATA_FILE
        display_data = el.DisplayData
        with data_path.open("rb") as f:
            display_data = pickle.load(f)
        [row_idx, col_idx] = update_data["pos"]
        for df, start_pos in display_data.dfs:
            rel_pos = df._get_cell_index_from_display_pos((row_idx, col_idx), start_pos)
            if rel_pos is not None:
                (rel_row_idx, rel_col_idx) = rel_pos
                df[df.columns[rel_col_idx]][rel_row_idx] = float(update_data["value"])

        with data_path.open("wb") as f:
            pickle.dump(display_data, f)

        dfs_json = el.to_json(
            display_data.dfs,
            include_header=True,
            sheet_styler=display_data.sheet_styler,
        )
        return dfs_json

    @app.route("/api/load", methods=["POST"])
    def load_file():
        data_path = cwd / DATA_FILE
        load_file_data = request.get_json()
        script_path = (cwd / load_file_data["path"]).expanduser().resolve()

        subprocess.run([sys.executable, str(script_path)], cwd=str(cwd))
        display_data: el.DisplayData
        with data_path.open("rb") as f:
            display_data = pickle.load(f)

        dfs_json = el.to_json(
            display_data.dfs,
            include_header=True,
            sheet_styler=display_data.sheet_styler,
        )
        resp = make_response(dfs_json)
        resp.set_cookie("script_path", str(script_path))
        return resp

    @app.route("/api/save", methods=["POST"])
    def save_file():
        data_path = cwd / DATA_FILE
        save_file_data = request.get_json()
        save_path = Path(save_file_data["filename"]).expanduser().resolve()
        display_data: el.DisplayData
        with data_path.open("rb") as f:
            display_data = pickle.load(f)
        el.to_excel(display_data.dfs, save_path, index_path=Path("index.json"))
        return {}

    return app
