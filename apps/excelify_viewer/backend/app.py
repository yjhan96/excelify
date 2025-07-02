import json
import pickle
import subprocess
import sys
from pathlib import Path

import grpc
from flask import Flask, make_response, request, send_from_directory
from flask_cors import CORS
from google.protobuf import json_format

import excelify as el
from apps.excelify_viewer.protos import rpc_pb2, rpc_pb2_grpc

DATA_FILE = ".excelify-data/data.pickle"


def create_app(file_path: str, cwd_str: str):
    cwd = Path(cwd_str)
    app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
    app.config["DEBUG"] = True
    grpc_channel = grpc.insecure_channel("localhost:50051")
    rpc_stub = rpc_pb2_grpc.ExcelifyViewerStub(grpc_channel)
    CORS(app)

    @app.route("/")
    def serve_react_app():
        assert app.static_folder is not None
        return send_from_directory(app.static_folder, "index.html")

    @app.put("/api/reload")
    def reset():
        script_path = request.cookies.get("script_path")
        assert script_path is not None

        resp = rpc_stub.Reload(rpc_pb2.ReloadRequest(script_path=script_path))
        dfs_json = json.loads(json_format.MessageToJson(resp.table))
        return dfs_json

    @app.route("/api/sheet")
    def get_sheet():
        script_path = request.cookies.get("script_path", str(file_path))
        resp = rpc_stub.GetSheet(rpc_pb2.GetSheetRequest(script_path=script_path))
        dfs_json = json.loads(json_format.MessageToJson(resp.table))
        resp = make_response(dfs_json)
        if script_path is not None:
            resp.set_cookie("script_path", script_path)
        return resp

    @app.put("/api/update")
    def update_cell():
        update_data = request.get_json()
        script_path = request.cookies.get("script_path")
        assert script_path is not None

        [row_idx, col_idx] = update_data["pos"]
        value = update_data["value"]
        resp = rpc_stub.UpdateCell(
            rpc_pb2.UpdateCellRequest(
                script_path=script_path,
                pos=rpc_pb2.Position(row=row_idx, col=col_idx),
                value=float(value),
            )
        )
        dfs_json = json.loads(json_format.MessageToJson(resp.table))
        return dfs_json

    @app.route("/api/load", methods=["POST"])
    def load_file():
        script_path = request.get_json()["path"]
        resp = rpc_stub.LoadFile(rpc_pb2.LoadFileRequest(script_path=script_path))
        dfs_json = json.loads(json_format.MessageToJson(resp.table))
        resp = make_response(dfs_json)
        resp.set_cookie("script_path", str(script_path))
        return resp

    @app.route("/api/save", methods=["POST"])
    def save_file():
        script_path = request.cookies.get("script_path")
        assert script_path is not None
        save_file_path = request.get_json()["filename"]

        rpc_stub.SaveFile(
            rpc_pb2.SaveFileRequest(
                script_path=script_path,
                file_path=save_file_path,
            )
        )
        return {}

    return app
