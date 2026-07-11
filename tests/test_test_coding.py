import os
import sys
import pytest
from src.agent import graph

def test_auto_repair_integration(tmp_path):
    """Test that the src agent can fix a bug in a file so that the test passes."""
    # 1. Create a buggy code file
    buggy_code = """def add_five(x):
    # This should be x + 5, but we write x + 4 as a bug
    return x + 4
"""
    source_file = tmp_path / "buggy_source.py"
    source_file.write_text(buggy_code, encoding="utf-8")
    
    # 2. Create a test file
    # We must explicitly add the temporary path to sys.path so the test runner can find buggy_source
    test_code = f"""import sys
sys.path.insert(0, r"{str(tmp_path)}")

from buggy_source import add_five

def test_add_five():
    assert add_five(10) == 15
"""
    test_file = tmp_path / "test_buggy_source.py"
    test_file.write_text(test_code, encoding="utf-8")
    
    # 3. Invoke the LangGraph workflow
    inputs = {
        "file_path": str(source_file),
        "test_path": str(test_file),
        "max_iterations": 3,
        "iterations": 0,
        "messages": [],
    }
    
    from unittest.mock import patch
    from langchain_core.messages import AIMessage
    
    mock_response = AIMessage(content="""```python
def add_five(x):
    # Corrected function
    return x + 5
```""")
    
    with patch("langchain_core.language_models.chat_models.BaseChatModel.invoke", return_value=mock_response):
        output = graph.invoke(inputs)
    
    # 4. Verify outcomes
    assert output["test_passed"] is True
    assert output["iterations"] > 0
    
    # Check that the file was corrected
    with open(source_file, "r", encoding="utf-8") as f:
        corrected_content = f.read()
        
    assert "return x + 5" in corrected_content


def test_ast_check_invalid_syntax(tmp_path):
    """Test that the agent flags syntax errors and invokes repair."""
    # 1. Create a file with syntactic errors (missing colon after function signature)
    syntax_error_code = """def add_five(x)
    return x + 5
"""
    source_file = tmp_path / "broken_syntax.py"
    source_file.write_text(syntax_error_code, encoding="utf-8")
    
    test_code = f"""import sys
sys.path.insert(0, r"{str(tmp_path)}")
from broken_syntax import add_five
def test_add_five():
    assert add_five(10) == 15
"""
    test_file = tmp_path / "test_broken_syntax.py"
    test_file.write_text(test_code, encoding="utf-8")
    
    # 2. Invoke the LangGraph workflow
    inputs = {
        "file_path": str(source_file),
        "test_path": str(test_file),
        "max_iterations": 3,
        "iterations": 0,
        "messages": [],
    }
    
    from unittest.mock import patch
    from langchain_core.messages import AIMessage
    
    mock_response = AIMessage(content="""```python
def add_five(x):
    return x + 5
```""")
    
    with patch("langchain_core.language_models.chat_models.BaseChatModel.invoke", return_value=mock_response):
        output = graph.invoke(inputs)
        
    # 3. Verify outcomes
    assert output["syntax_passed"] is True
    assert output["test_passed"] is True
    assert output["iterations"] == 1


def test_validation_errors(tmp_path):
    """Test that entry validation flags incorrect or missing inputs."""
    # 1. Missing file_path
    inputs = {
        "max_iterations": 3,
        "iterations": 0,
        "messages": [],
    }
    output = graph.invoke(inputs)
    assert output["validation_passed"] is False
    assert "Missing required field 'file_path'" in output["error_message"]

    # 2. File does not exist
    inputs = {
        "file_path": "non_existent_file.py",
        "max_iterations": 3,
        "iterations": 0,
        "messages": [],
    }
    output = graph.invoke(inputs)
    assert output["validation_passed"] is False
    assert "does not exist on disk" in output["error_message"]

    # 3. Existing file but missing both test_path and test_description
    source_file = tmp_path / "valid_file.py"
    source_file.write_text("def ok(): pass", encoding="utf-8")
    inputs = {
        "file_path": str(source_file),
        "max_iterations": 3,
        "iterations": 0,
        "messages": [],
    }
    output = graph.invoke(inputs)
    assert output["validation_passed"] is False
    assert "Missing both 'test_path' and 'test_description'" in output["error_message"]


def test_generate_test_and_review(tmp_path):
    """Test the generation of tests from description and the user approval/feedback loops."""
    # 1. Setup buggy code file
    buggy_code = """def multiply(a, b):
    return a * b
"""
    source_file = tmp_path / "calc.py"
    source_file.write_text(buggy_code, encoding="utf-8")

    inputs = {
        "file_path": str(source_file),
        "test_description": "Verify multiply function correctly multiplies negative numbers",
        "max_iterations": 3,
        "iterations": 0,
        "messages": [],
    }

    # 2. Invoke the LangGraph workflow using the real LLM (Ollama)
    from unittest.mock import patch
    # Mock human input to return 'y' (approve)
    with patch("builtins.input", return_value="y") as mock_input:
        output = graph.invoke(inputs)

    assert output["validation_passed"] is True
    assert output["test_path"] is not None
    assert os.path.exists(output["test_path"])
    assert output["test_passed"] is True
    mock_input.assert_called_once()


