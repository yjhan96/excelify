import os
import subprocess
import sys
from pathlib import Path

import click


def get_repo_root() -> Path:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    return Path(repo_root)


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
    repo_root = get_repo_root()
    executable_path = Path(sys.executable)
    webapp_dir = repo_root
    webapp_cmd = [
        executable_path,
        "-m",
        "flask",
        "--app",
        f'apps.excelify_viewer.backend.app:create_app("{file_path}", "{Path.cwd()}")',
        "run",
        "--no-debugger",
        "--debug",
    ]
    server_command = [
        executable_path,
        "-m",
        "apps.excelify_viewer.server.server",
        "--working-dir",
        ".",
        "--file-path",
        str(file_path),
    ]
    backend_subprocess: subprocess.Popen | None = None
    server_subprocess: subprocess.Popen | None = None
    try:
        backend_subprocess = subprocess.Popen(
            webapp_cmd,
            cwd=str(webapp_dir),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        server_subprocess = subprocess.Popen(
            server_command,
            cwd=str(repo_root),
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
