from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """The state of the self-correcting code repair agent."""
    file_path: str
    test_path: str
    code: str
    test_logs: str
    test_passed: bool
    syntax_passed: bool
    iterations: int
    max_iterations: int
    messages: Annotated[Sequence[BaseMessage], add_messages]
    test_description: str
    validation_passed: bool
    error_message: str
    review_feedback: str
