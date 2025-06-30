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
    webapp_dir = repo_root / "apps" / "excelify-viewer" / "backend"
    webapp_cmd = [
        executable_path,
        "-m",
        "flask",
        "--app",
        f'app:create_app("{file_path}", "{Path.cwd()}")',
        "run",
        "--no-debugger",
        "--debug",
    ]
    backend_subprocess: subprocess.Popen | None = None
    try:
        backend_subprocess = subprocess.Popen(
            webapp_cmd,
            cwd=str(webapp_dir),
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        for p in [backend_subprocess]:
            p.wait()
    except Exception as e:
        print(f"Received the following error: {e}", file=sys.stderr)
    finally:
        print("Shutting down applications...")
        shutdown_process(backend_subprocess, "backend process")


if __name__ == "__main__":
    main()
