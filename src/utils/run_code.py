import subprocess
import sys
import tempfile
import os

def run_code(test_code: str) -> dict:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", tmp_path, "-v"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "output": (result.stdout + result.stderr).strip(),
        }
    finally:
        os.unlink(tmp_path)
