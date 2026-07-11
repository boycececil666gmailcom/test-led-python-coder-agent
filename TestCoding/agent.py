from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START
from TestCoding.state import AgentState
from TestCoding.nodes import (
    node_run_tests,
    node_generate_code,
    node_check_syntax,
    cond_should_continue,
    cond_after_syntax_check,
)


# Define the state graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("node_run_tests", node_run_tests)
workflow.add_node("node_generate_code", node_generate_code)
workflow.add_node("node_check_syntax", node_check_syntax)

# Set entry point
workflow.add_edge(START, "node_check_syntax")

# Add conditional edge from node_check_syntax
workflow.add_conditional_edges(
    "node_check_syntax",
    cond_after_syntax_check,
)

# Add conditional edge from node_run_tests
workflow.add_conditional_edges(
    "node_run_tests",
    cond_should_continue,
)

# Add normal edge from node_generate_code to node_check_syntax
workflow.add_edge("node_generate_code", "node_check_syntax")

# Compile graph
graph = workflow.compile()
