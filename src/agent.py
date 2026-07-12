from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes import (
    node_run_tests,
    node_generate_code,
    node_check_syntax,
    cond_should_continue,
    cond_after_syntax_check,
    node_validate_inputs,
    cond_route_entry,
    node_generate_test,
    node_human_review,
    cond_after_review,
)


# Define the state graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("node_validate_inputs", node_validate_inputs)
workflow.add_node("node_generate_test", node_generate_test)
workflow.add_node("node_human_review", node_human_review)
workflow.add_node("node_run_tests", node_run_tests)
workflow.add_node("node_generate_code", node_generate_code)
workflow.add_node("node_check_syntax", node_check_syntax)

# Set entry point
workflow.add_edge(START, "node_validate_inputs")

# Add conditional edge from validation entry point
workflow.add_conditional_edges(
    "node_validate_inputs",
    cond_route_entry,
    {
        "END": END,
        "node_check_syntax": "node_check_syntax",
        "node_generate_test": "node_generate_test",
    }
)

# Add edge from node_generate_test to node_human_review
workflow.add_edge("node_generate_test", "node_human_review")

# Add conditional edge from human review
workflow.add_conditional_edges(
    "node_human_review",
    cond_after_review,
    {
        "END": END,
        "node_check_syntax": "node_check_syntax",
        "node_generate_test": "node_generate_test",
    }
)

# Add conditional edge from node_check_syntax
workflow.add_conditional_edges(
    "node_check_syntax",
    cond_after_syntax_check,
    {
        "node_generate_code": "node_generate_code",
        "node_run_tests": "node_run_tests",
    }
)

# Add conditional edge from node_run_tests
workflow.add_conditional_edges(
    "node_run_tests",
    cond_should_continue,
    {
        END: END,
        "node_generate_code": "node_generate_code",
    }
)

# Add normal edge from node_generate_code to node_check_syntax
workflow.add_edge("node_generate_code", "node_check_syntax")

# Compile graph
graph = workflow.compile(name="PythonCoderAgent")

