from typing import Annotated, Sequence, TypedDict, NotRequired
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """The state of the self-correcting code repair agent."""
    file_path: str
    max_iterations: int
    
    messages: NotRequired[Annotated[Sequence[BaseMessage], add_messages]]
    iterations: NotRequired[int]
    test_path: NotRequired[str]
    test_description: NotRequired[str]
    code: NotRequired[str]
    test_logs: NotRequired[str]
    test_passed: NotRequired[bool]
    syntax_passed: NotRequired[bool]
    validation_passed: NotRequired[bool]
    error_message: NotRequired[str]
    review_feedback: NotRequired[str]
