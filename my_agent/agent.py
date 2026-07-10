from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from my_agent.state import AgentState
from my_agent.nodes import call_model
from my_agent.tools import tools

def should_continue(state: AgentState):
    """Determine whether to route to the tool executor node or end the run."""
    messages = state["messages"]
    last_message = messages[-1]
    # If the model requested tool calls, go to tools
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    # Otherwise, we stop
    return END

# Define a new StateGraph
workflow = StateGraph(AgentState)  # type: ignore[arg-type]

# Add the two nodes we will alternate between
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Set the entrypoint to "agent"
workflow.add_edge(START, "agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use "agent".
    # This means these edges will be evaluated after the "agent" node is run.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
)

# We now add a normal edge from `tools` to `agent`.
# This means after `tools` is called, `agent` node is called next.
workflow.add_edge("tools", "agent")

# Compile the graph into a runnable graph
graph = workflow.compile()
