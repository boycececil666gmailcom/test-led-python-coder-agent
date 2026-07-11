import os
import sys
import pytest
from TestCoding.agent import graph

def test_auto_repair_integration(tmp_path):
    """Test that the TestCoding agent can fix a bug in a file so that the test passes."""
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
