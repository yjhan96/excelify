import json
from pathlib import Path

import grpc
from flask import Flask, redirect, request, send_from_directory, url_for
from flask_cors import CORS
from google.protobuf import json_format

from apps.excelify_viewer.protos import rpc_pb2, rpc_pb2_grpc

DATA_FILE = ".excelify-data/data.pickle"


def create_app(file_path: str, cwd_str: str):
    app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
    app.config["DEBUG"] = True
    grpc_channel = grpc.insecure_channel("localhost:50051")
    rpc_stub = rpc_pb2_grpc.ExcelifyViewerStub(grpc_channel)
    CORS(app)

    @app.route("/")
    def serve_react_app():
        return redirect(url_for("print_sheetname", sheet_name=file_path))

    @app.route("/sheet/<path:sheet_name>")
    def print_sheetname(sheet_name):
        assert app.static_folder is not None
        return send_from_directory(app.static_folder, "index.html")

    @app.put("/api/reload")
    def reset():
        reset_request = request.get_json()
        script_path = reset_request["scriptPath"]
        assert script_path is not None
        script_path = Path(script_path).resolve()

        resp = rpc_stub.Reload(rpc_pb2.ReloadRequest(script_path=str(script_path)))
        dfs_json = json.loads(json_format.MessageToJson(resp.table))
        return dfs_json

    @app.get("/api/sheet")
    def get_sheet():
        script_path = request.args.get("scriptPath")
        assert script_path is not None
        script_path = Path(script_path).resolve()
        resp = rpc_stub.GetSheet(rpc_pb2.GetSheetRequest(script_path=str(script_path)))
        return json.loads(json_format.MessageToJson(resp.table))

    @app.put("/api/update")
    def update_cell():
        update_data = request.get_json()
        script_path = update_data["scriptPath"]
        assert script_path is not None
        script_path = Path(script_path).resolve()

        [row_idx, col_idx] = update_data["pos"]
        value = update_data["value"]
        resp = rpc_stub.UpdateCell(
            rpc_pb2.UpdateCellRequest(
                script_path=str(script_path),
                pos=rpc_pb2.Position(row=row_idx, col=col_idx),
                value=float(value),
            )
        )
        dfs_json = json.loads(json_format.MessageToJson(resp.table))
        return dfs_json

    @app.route("/api/save", methods=["POST"])
    def save_file():
        save_file_request = request.get_json()
        script_path = Path(save_file_request["scriptPath"]).resolve()
        save_file_path = save_file_request["filename"]
        assert script_path is not None

        rpc_stub.SaveFile(
            rpc_pb2.SaveFileRequest(
                script_path=str(script_path),
                file_path=save_file_path,
            )
        )
        return {}

    return app
