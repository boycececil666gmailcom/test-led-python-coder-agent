from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers together. Use this tool when you need to calculate a product."""
    return a * b

# List of tools available to the agent
tools = [multiply]
