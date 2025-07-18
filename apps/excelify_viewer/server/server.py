import pickle
import subprocess
import sys
from concurrent import futures
from pathlib import Path

import click
import grpc
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Struct

import excelify as el
from apps.excelify_viewer.protos import rpc_pb2, rpc_pb2_grpc

DATA_FILE = ".excelify-data/data.pickle"


class ExcelifyViewerServer(rpc_pb2_grpc.ExcelifyViewerServicer):
    def __init__(self, working_dir: Path, file_path: Path) -> None:
        self.file_path = file_path
        self.working_dir = working_dir
        self.scripts_to_data = {}

    def _run_script(self, script_path: Path) -> el.DisplayData:
        data_path = self.working_dir / DATA_FILE
        subprocess.run([sys.executable, script_path], cwd=str(self.working_dir))

        with data_path.open("rb") as f:
            display_data: el.DisplayData = pickle.load(f)
        return display_data

    def Reload(self, request, context):
        script_path = Path(request.script_path).resolve()
        display_data = self._run_script(script_path)
        self.scripts_to_data[script_path] = display_data
        dfs_json = el.to_json(
            display_data.dfs,
            include_header=True,
            sheet_styler=display_data.sheet_styler,
        )
        table = Struct()
        json_format.ParseDict(dfs_json, table)
        return rpc_pb2.ReloadResponse(table=table)

    def GetSheet(self, request, context):
        script_path = Path(request.script_path).resolve()
        display_data: el.DisplayData
        if script_path in self.scripts_to_data:
            display_data = self.scripts_to_data[script_path]
        else:
            display_data = self._run_script(script_path)
            self.scripts_to_data[script_path] = display_data

        dfs_json = el.to_json(
            display_data.dfs,
            include_header=True,
            sheet_styler=display_data.sheet_styler,
        )
        table = Struct()
        json_format.ParseDict(dfs_json, table)
        return rpc_pb2.GetSheetResponse(table=table)

    def UpdateCell(self, request, context):
        script_path = Path(request.script_path).resolve()
        row_idx, col_idx = request.pos.row, request.pos.col
        if script_path not in self.scripts_to_data:
            raise ValueError(
                f"Following script doesn't have data already stored: {script_path}"
            )
        display_data = self.scripts_to_data[script_path]

        for df, start_pos in display_data.dfs:
            rel_pos = df._get_cell_index_from_display_pos((row_idx, col_idx), start_pos)
            if rel_pos is not None:
                (rel_row_idx, rel_col_idx) = rel_pos
                df[df.columns[rel_col_idx]][rel_row_idx] = float(request.value)

        dfs_json = el.to_json(
            display_data.dfs,
            include_header=True,
            sheet_styler=display_data.sheet_styler,
        )
        table = Struct()
        json_format.ParseDict(dfs_json, table)
        return rpc_pb2.UpdateCellResponse(table=table)

    def LoadFile(self, request, context):
        script_path = (self.working_dir / request.script_path).resolve()
        display_data = self._run_script(script_path)
        self.scripts_to_data[script_path] = display_data
        dfs_json = el.to_json(
            display_data.dfs,
            include_header=True,
            sheet_styler=display_data.sheet_styler,
        )
        table = Struct()
        json_format.ParseDict(dfs_json, table)
        return rpc_pb2.LoadFileResponse(table=table)

    def SaveFile(self, request, context):
        script_path = Path(request.script_path).resolve()
        file_path = (self.working_dir / request.file_path).resolve()
        if script_path not in self.scripts_to_data:
            raise ValueError(
                f"Following script doesn't have data already stored: {script_path}"
            )
        display_data = self.scripts_to_data[script_path]
        el.to_excel(
            display_data.dfs,
            file_path,
            index_path=(file_path.parent / "index.json"),
            sheet_styler=display_data.sheet_styler,
        )
        return rpc_pb2.SaveFileResponse()


@click.command()
@click.option("--working-dir", required=True, help="working directory")
@click.option("--file-path", required=True, help="default file path")
def serve(working_dir, file_path):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc_pb2_grpc.add_ExcelifyViewerServicer_to_server(
        ExcelifyViewerServer(Path(working_dir), Path(file_path)), server
    )
    server.add_insecure_port("localhost:50051")
    print("Starting the excelify_viewer server...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
