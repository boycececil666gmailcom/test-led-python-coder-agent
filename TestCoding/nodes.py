import os
import sys
import subprocess
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from TestCoding.state import AgentState
from langgraph.graph import END

# Load env variables if running standalone
load_dotenv()

# Initialize LLM
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def run_tests(state: AgentState) -> dict:
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

def generate_code(state: AgentState) -> dict:
    """Generate corrected code based on current code and test logs, then write to file."""
    file_path = state.get("file_path")
    code = state.get("code", "")
    test_logs = state.get("test_logs", "")
    iterations = state.get("iterations", 0)
    
    prompt = f"""You are a code repair agent. The tests for the code have failed.
Your task is to fix the bug in the code so that the tests pass.

Here is the path to the file to modify:
{file_path}

Here is the current source code:
```python
{code}
```

Here are the pytest logs showing the failures:
```
{test_logs}
```

Please output the entire corrected code. Wrap the code in a python markdown code block (i.e. starting with ```python and ending with ```).
Do not explain the changes, just output the corrected python file content.
"""
    
    response = model.invoke([HumanMessage(content=prompt)])
    response_content = response.content
    
    # Extract code from the markdown code block if present
    corrected_code = response_content
    if "```python" in corrected_code:
        corrected_code = corrected_code.split("```python")[1].split("```")[0]
    elif "```" in corrected_code:
        corrected_code = corrected_code.split("```")[1].split("```")[0]
        
    corrected_code = corrected_code.strip()
    
    # Write corrected code back to file
    if file_path:
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(corrected_code)
            
    return {
        "code": corrected_code,
        "iterations": iterations + 1,
        "messages": [response]
    }

def should_continue(state: AgentState):
    """Determine the next step based on test result and iterations."""
    test_passed = state.get("test_passed", False)
    iterations = state.get("iterations", 0)
    max_iterations = state.get("max_iterations", 3)
    
    if test_passed:
        return END
    
    if iterations >= max_iterations:
        return END
        
    return "generate_code"
