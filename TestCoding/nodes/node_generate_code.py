import os
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from TestCoding.state import AgentState



# Initialize LLM dynamically from environment variables (Mandatory)
model_name = os.environ.get("LLM_MODEL")
base_url = os.environ.get("LLM_BASE_URL")
api_key = os.environ.get("LLM_API_KEY")

if not model_name or not base_url or not api_key:
    missing_vars = []
    if not model_name:
        missing_vars.append("LLM_MODEL")
    if not base_url:
        missing_vars.append("LLM_BASE_URL")
    if not api_key:
        missing_vars.append("LLM_API_KEY")
    raise ValueError(
        f"Missing mandatory LLM configuration environment variable(s): {', '.join(missing_vars)}. "
        "Please define them in your environment or .env file."
    )

model = ChatOpenAI(
    model=model_name,
    base_url=base_url,
    api_key=api_key,
    temperature=0
)



def node_generate_code(state: AgentState) -> dict:
    """Generate corrected code based on current code and test logs, then write to file."""
    file_path = state.get("file_path")
    code = state.get("code", "")
    test_logs = state.get("test_logs", "")
    iterations = state.get("iterations", 0)
    syntax_passed = state.get("syntax_passed", True)
    
    # Dynamically inject context about whether it's a syntax or logic error
    if not syntax_passed:
        error_context = "CRITICAL: The code failed to parse due to a SYNTAX error. Please locate the syntax/parsing issue and fix it."
    else:
        error_context = "CRITICAL: The code has valid Python syntax, but failed the test assertions (LOGIC error). Please check the test failures and correct the logic."
    
    prompt = f"""You are a code repair agent. The tests for the code have failed.
Your task is to fix the bug in the code so that the tests pass.

{error_context}

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
    response_content = StrOutputParser().invoke(response)
        
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
