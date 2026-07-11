import os
from src.state import AgentState

def node_validate_inputs(state: AgentState) -> dict:
    """Validate that the target file path exists and that either a test path or a description is provided."""
    file_path = state.get("file_path")
    test_path = state.get("test_path")
    test_description = state.get("test_description")

    # 1. Check file_path
    if not file_path:
        return {
            "validation_passed": False,
            "error_message": "Missing required field 'file_path'."
        }
    
    if not os.path.exists(file_path):
        return {
            "validation_passed": False,
            "error_message": f"Target file '{file_path}' does not exist on disk."
        }

    # 2. Check test_path or test_description
    if not test_path and not test_description:
        return {
            "validation_passed": False,
            "error_message": "Missing both 'test_path' and 'test_description'. You must provide one."
        }

    return {
        "validation_passed": True,
        "error_message": ""
    }
