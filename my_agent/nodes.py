import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from my_agent.state import AgentState
from my_agent.tools import tools

# Load env variables if running standalone
load_dotenv()

# Set up model and bind tools using local Ollama server
# By default, Ollama hosts an OpenAI-compatible API at http://localhost:11434/v1
model = ChatOpenAI(
    model="qwen2.5:7b",
    temperature=0,
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Ollama does not require a real API key, but a placeholder is needed
)
model_with_tools = model.bind_tools(tools)

def call_model(state: AgentState):
    """Invoke the LLM to get the next agent action or final response."""
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    # We return a list containing the response, which will be appended to the existing state
    return {"messages": [response]}
