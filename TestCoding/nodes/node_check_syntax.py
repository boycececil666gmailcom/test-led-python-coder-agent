
import os
import ast
from TestCoding.state import AgentState

def node_check_syntax(state: AgentState) -> dict:
    """Validate python code structure before running pytest."""
    file_path = state.get("file_path")
    
    code = ""
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
            
    try:
        ast.parse(code)
        return {
            "code": code,
            "syntax_passed": True,
        }
    except SyntaxError as e:
        error_msg = f"SyntaxError: {e.msg} on line {e.lineno} col {e.offset}\nCode: {e.text}"
        return {
            "code": code,
            "syntax_passed": False,
            "test_logs": error_msg,
            "test_passed": False,
        }
