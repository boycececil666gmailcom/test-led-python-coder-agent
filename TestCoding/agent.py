from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START
from TestCoding.state import AgentState
from TestCoding.nodes import node_run_tests, node_generate_code, cond_should_continue


# Define the state graph
workflow = StateGraph(AgentState) # type: ignore[arg-type]

# Add nodes
workflow.add_node("node_run_tests", node_run_tests)
workflow.add_node("node_generate_code", node_generate_code)

# Set entry point
workflow.add_edge(START, "node_run_tests")

# Add conditional edge from node_run_tests
workflow.add_conditional_edges(
    "node_run_tests",
    cond_should_continue,
)

# Add normal edge from node_generate_code to node_run_tests
workflow.add_edge("node_generate_code", "node_run_tests")

# Compile graph
graph = workflow.compile()
