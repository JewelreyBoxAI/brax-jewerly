from typing import List, TypedDict, NotRequired
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    user_id: str
    thread_id: str
    trace_id: NotRequired[str]