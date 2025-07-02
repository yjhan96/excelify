import grpc

from apps.excelify_viewer.protos import rpc_pb2, rpc_pb2_grpc


def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = rpc_pb2_grpc.ExcelifyViewerStub(channel)
        resp = stub.Reload(rpc_pb2.ReloadRequest(script_path="hi"))
        print(resp.res)


if __name__ == "__main__":
    main()
