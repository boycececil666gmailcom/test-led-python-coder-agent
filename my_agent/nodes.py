import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from my_agent.state import AgentState
from my_agent.tools import tools

# Load env variables if running standalone
load_dotenv()

# Set up model and bind tools
# By default, uses gpt-4o-mini. Ensure OPENAI_API_KEY is in your environment.
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
model_with_tools = model.bind_tools(tools)

def call_model(state: AgentState):
    """Invoke the LLM to get the next agent action or final response."""
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    # We return a list containing the response, which will be appended to the existing state
    return {"messages": [response]}
