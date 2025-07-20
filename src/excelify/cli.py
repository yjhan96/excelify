# Copyright 2025 Albert Han
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import sys
from pathlib import Path

import click


def shutdown_process(child_process: subprocess.Popen | None, process_name: str):
    if child_process is None or child_process.poll() is not None:
        return

    print(f"Terminating {process_name}...")
    child_process.terminate()
    child_process.wait(timeout=5)
    if child_process.poll() is not None:
        print(f"Killing {process_name}...")
        child_process.kill()


@click.command()
@click.option("--file-path", required=True, help="file path")
def main(file_path):
    executable_path = Path(sys.executable)
    cwd = Path.cwd()
    webapp_cmd = [
        executable_path,
        "-m",
        "flask",
        "--app",
        f'apps.excelify_viewer.backend.app:create_app("{file_path}", "{cwd}")',
        "run",
        "--no-debugger",
        "--debug",
    ]
    server_command = [
        executable_path,
        "-m",
        "apps.excelify_viewer.server.server",
        "--working-dir",
        str(cwd),
        "--file-path",
        str(file_path),
    ]
    backend_subprocess: subprocess.Popen | None = None
    server_subprocess: subprocess.Popen | None = None
    try:
        backend_subprocess = subprocess.Popen(
            webapp_cmd,
            cwd=str(cwd),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        server_subprocess = subprocess.Popen(
            server_command,
            cwd=str(cwd),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        for p in [backend_subprocess, server_subprocess]:
            p.wait()
    except Exception as e:
        print(f"Received the following error: {e}", file=sys.stderr)
    finally:
        print("Shutting down applications...")
        shutdown_process(backend_subprocess, "backend process")
        shutdown_process(server_subprocess, "server process")


if __name__ == "__main__":
    main()
