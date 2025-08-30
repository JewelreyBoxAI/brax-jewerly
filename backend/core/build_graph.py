from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, AIMessage
from .state import AgentState
from .agent_adapter import AgenticCoreAdapter
import logging

log = logging.getLogger("build_graph")

def create_brax_chat_graph():
    """Build the conversation graph for Brax chatbot."""
    
    adapter = AgenticCoreAdapter()
    
    async def agent_node(state: AgentState) -> AgentState:
        """Main agent processing node."""
        try:
            messages = state["messages"]
            user_id = state["user_id"]
            thread_id = state["thread_id"]
            
            # Get the latest user message
            if not messages or not isinstance(messages[-1], BaseMessage):
                raise ValueError("No valid user message found")
            
            last_message = messages[-1].content
            
            # Process through the adapter
            result = await adapter.process_message(
                thread_id=thread_id,
                user_message=last_message,
                context={"user_id": user_id}
            )
            
            # Create AI response message
            ai_message = AIMessage(content=result["response"])
            
            # Update state with new message
            new_messages = messages + [ai_message]
            
            return {
                **state,
                "messages": new_messages
            }
            
        except Exception as e:
            log.error(f"Agent node error: {str(e)}")
            error_message = AIMessage(content="I apologize for the technical difficulty. Please try again.")
            return {
                **state,
                "messages": state["messages"] + [error_message]
            }
    
    # Build the graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    
    return workflow.compile()