import os
import sys
import subprocess
from TestCoding.state import AgentState

def node_run_tests(state: AgentState) -> dict:
    """Run pytest on the test path, capture logs, and update the state."""
    file_path = state.get("file_path")
    test_path = state.get("test_path")
    
    # Read the current code from file_path if it exists to populate state
    code = ""
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

    if not test_path:
        return {
            "code": code,
            "test_logs": "No test path specified.",
            "test_passed": False,
        }

    # Set up environment variables to make sure python path includes workspace root
    env = os.environ.copy()
    # TestCoding is one level down from workspace root
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env["PYTHONPATH"] = workspace_root + os.pathsep + env.get("PYTHONPATH", "")

    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path],
        capture_output=True,
        text=True,
        env=env
    )
    
    # Combine stdout and stderr
    test_logs = result.stdout + "\n" + result.stderr
    test_passed = result.returncode == 0
    
    return {
        "code": code,
        "test_logs": test_logs,
        "test_passed": test_passed,
    }
