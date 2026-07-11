from TestCoding.state import AgentState

def cond_after_review(state: AgentState) -> str:
    """Route based on user input from the review node."""
    feedback = state.get("review_feedback")
    
    if feedback == "exit":
        return "END"
    # This means the test passes the review
    elif feedback is None:
        return "node_check_syntax"
    
    # Any other string is treated as feedback -> regenerate test
    return "node_generate_test"
