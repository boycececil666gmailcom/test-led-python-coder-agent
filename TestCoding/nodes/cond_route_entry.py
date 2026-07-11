from TestCoding.state import AgentState

def cond_route_entry(state: AgentState) -> str:
    """Route from entry validation based on input correctness and available fields."""
    if not state.get("validation_passed", False):
        return "END"
    
    # If we have a test path already, check syntax of code first
    if state.get("test_path"):
        return "node_check_syntax"
        
    # Otherwise we generate tests from description
    return "node_generate_test"
