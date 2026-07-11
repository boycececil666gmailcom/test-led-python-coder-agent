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


def cond_after_syntax_check(state: AgentState) -> str:
    """Determine next step based on syntax check results."""
    syntax_passed = state.get("syntax_passed", True)
    iterations = state.get("iterations", 0)
    max_iterations = state.get("max_iterations", 3)
    
    if not syntax_passed:
        if iterations >= max_iterations:
            return END
        return "node_generate_code"
        
    return "node_run_tests"
