import subprocess
import sys

from langchain_core.tools import tool
from langgraph.types import Command
from langchain.tools import ToolRuntime

@tool
def run_code(test_code: str, runtime: ToolRuntime) -> str:
    """
    Executes the provided test code and returns the output.
    Stores results in graph state under status and output keys.

    Args: 
        test_code (str): The code to be executed.
    Returns:
        str: The output from executing the code, including stdout, stderr, and exit code.
    
    """
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0 and not result.stderr:
        new_status = "success"
        new_output = result.stdout.strip()
    else:
        new_status = "failed"
        new_output = f"Error (code {result.returncode}):\n{result.stderr or result.stdout}"

    return Command(
        update={
            "status": new_status,
            "output": new_output,
        }
    )
