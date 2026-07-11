import os
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from src.state import AgentState

# Initialize LLM dynamically from environment variables
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
    temperature=0.1
)

def node_generate_test(state: AgentState) -> dict:
    """Generate a pytest file based on the target source code, test description, and optional feedback."""
    file_path = state.get("file_path")
    code = state.get("code", "")
    test_description = state.get("test_description", "")
    review_feedback = state.get("review_feedback")
    
    # If code is not loaded in state, load it from file_path
    if not code and file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

    # Determine test path if not set yet
    test_path = state.get("test_path")
    if not test_path:
        dir_name = os.path.dirname(os.path.abspath(file_path))
        base_name = os.path.basename(file_path)
        # Prefix the target file's basename with 'test_'
        test_path = os.path.join(dir_name, "test_" + base_name)

    # Build prompt
    feedback_clause = ""
    if review_feedback:
        feedback_clause = f"""
CRITICAL: The user reviewed the previously generated test script and REJECTED it.
They provided the following feedback/corrections to be applied to the test script:
{review_feedback}
"""

    prompt = f"""You are a test generation agent.
Your task is to write a comprehensive suite of `pytest` test cases to verify the target Python file.

Here is the path to the target file:
{file_path}

Here is the current source code:
```python
{code}
```

The user wants the tests to verify the following behavior/requirements:
{test_description}
{feedback_clause}

Please output the entire python code for the `pytest` test script. 
Ensure the tests import the functions or classes from the target file properly. If the target file is named `foo.py`, you can import from it using `from foo import ...` or `import foo`.
Wrap the code in a python markdown code block (i.e. starting with ```python and ending with ```).
Do not explain the tests, just output the test code.
"""

    response = model.invoke([HumanMessage(content=prompt)])
    response_content = StrOutputParser().invoke(response)
    
    test_code = response_content
    if "```python" in test_code:
        test_code = test_code.split("```python")[1].split("```")[0]
    elif "```" in test_code:
        test_code = test_code.split("```")[1].split("```")[0]
        
    test_code = test_code.strip()

    # Write generated test back to test_path
    os.makedirs(os.path.dirname(os.path.abspath(test_path)), exist_ok=True)
    with open(test_path, "w", encoding="utf-8") as f:
        f.write(test_code)

    return {
        "test_path": test_path,
        "code": code,
        "messages": [response]
    }
