from langgraph.graph import END
from TestCoding.state import AgentState

def cond_should_continue(state: AgentState) -> str:
    """Determine the next step based on test result and iterations."""
    test_passed = state.get("test_passed", False)
    iterations = state.get("iterations", 0)
    max_iterations = state.get("max_iterations", 3)
    
    if test_passed:
        return END
    
    if iterations >= max_iterations:
        return END
        
    return "node_generate_code"
