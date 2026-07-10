from langgraph.graph import StateGraph, START
from TestCoding.state import AgentState
from TestCoding.nodes import run_tests, generate_code, should_continue

# Define the state graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("run_tests", run_tests)
workflow.add_node("generate_code", generate_code)

# Set entry point
workflow.add_edge(START, "run_tests")

# Add conditional edge from run_tests
workflow.add_conditional_edges(
    "run_tests",
    should_continue,
)

# Add normal edge from generate_code to run_tests
workflow.add_edge("generate_code", "run_tests")

# Compile graph
graph = workflow.compile()
