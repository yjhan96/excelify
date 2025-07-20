from pathlib import Path
import shutil
import subprocess

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

FRONTEND_DIR = Path("apps/excelify_viewer/frontend")
DIST_DIR = FRONTEND_DIR / "dist"
PYTHON_PACKAGE_FRONTEND_DIST_DIR = Path("apps/excelify_viewer/backend/frontend_dist")

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        print(f"Building React app from {FRONTEND_DIR}...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=FRONTEND_DIR,
                check=True,
                capture_output=True,
                text=True
            )
            print("Node.js dependencies installed.")

            subprocess.run(
                ["npm", "run", "build"],
                cwd=FRONTEND_DIR,
                check=True,
                capture_output=True,
                text=True
            )
            print("React app built successfully.")

            if PYTHON_PACKAGE_FRONTEND_DIST_DIR.exists():
                print(f"Clearing existing {PYTHON_PACKAGE_FRONTEND_DIST_DIR}...")
                shutil.rmtree(PYTHON_PACKAGE_FRONTEND_DIST_DIR)
            shutil.copytree(DIST_DIR, PYTHON_PACKAGE_FRONTEND_DIST_DIR)
        except subprocess.CalledProcessError as e:
            print(f"Error building React app: {e.stderr}")
            raise RuntimeError(f"React build failed: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError("npm command not found. Make sure Node.js and npm are installed and in your PATH.")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred during React build hook: {e}")
