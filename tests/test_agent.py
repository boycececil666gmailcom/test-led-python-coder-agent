import pytest
from langchain_core.messages import HumanMessage, AIMessage
from my_agent.nodes import model, model_with_tools, call_model
from my_agent.state import AgentState
from my_agent.tools import multiply

def test_llm_basic_response():
    """Test that the LLM responds to basic greetings."""
    messages = [HumanMessage(content="Hello! Who are you?")]
    response = model.invoke(messages)
    assert isinstance(response.content, str)
    assert len(response.content) > 0

def test_llm_tool_calling():
    """Test that the LLM correctly requests to call the multiply tool when asked."""
    messages = [HumanMessage(content="What is 6 times 7?")]
    response = model_with_tools.invoke(messages)
    
    # Verify the model decides to call a tool
    assert response.tool_calls
    assert response.tool_calls[0]["name"] == "multiply"
    assert response.tool_calls[0]["args"] == {"a": 6, "b": 7}

from my_agent.agent import graph

def test_node_call_model():
    """Test the LangGraph node 'call_model' directly."""
    state = {
        "messages": [HumanMessage(content="Hello")]
    }
    result = call_model(state)
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)

def test_graph_end_to_end():
    """Test the compiled LangGraph workflow end-to-end."""
    inputs = {
        "messages": [HumanMessage(content="What is 6 times 8?")]
    }
    output = graph.invoke(inputs)
    
    # Assertions
    messages = output["messages"]
    assert len(messages) >= 3  # User message, Tool call message, Tool result, and/or final answer
    
    # Print out all the messages in the graph state
    print("\n--- Graph Message Flow ---")
    for i, message in enumerate(messages):
        print(f"Message {i} ({type(message).__name__}): {message.content}")
    print("--------------------------")

    # Check if the correct result "48" is in the conversation history
    found_answer = False
    for message in messages:
        if "48" in str(message.content):
            found_answer = True
            break
    assert found_answer, f"Did not find correct answer 48 in messages: {[m.content for m in messages]}"

