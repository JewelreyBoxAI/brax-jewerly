import logging, inspect, re, json
from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage

# Import your immutable core as-is. Adjust paths if different.
# from agents.agentic_mcp.mcp_voice_agent import AgenticMCP
# from memory.memory_manager import MemoryManager

log = logging.getLogger("agent_adapter")

class AgenticCoreAdapter:
    """Adapter that wraps your immutable AgenticMCP and MemoryManager without modifying them."""
    
    def __init__(self, agent_id: str | None = None):
        # self.agent = AgenticMCP(agent_id=agent_id)
        # self.memory = MemoryManager()
        self.agent_id = agent_id or "brax-concierge"
        log.info(f"Initialized AgenticCoreAdapter with agent_id: {self.agent_id}")
    
    async def process_message(self, thread_id: str, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user message through the agent and return structured response."""
        try:
            # Convert to LangChain message format
            human_msg = HumanMessage(content=user_message)
            
            # For demo purposes, we'll simulate the agent response
            # In production, replace this with actual calls to your AgenticMCP
            response_content = await self._simulate_agent_response(user_message, context or {})
            
            # Extract lead information from response if present
            lead_data = self._extract_lead_data(response_content)
            
            return {
                "response": response_content,
                "lead_data": lead_data,
                "thread_id": thread_id,
                "success": True
            }
            
        except Exception as e:
            log.error(f"Error processing message: {str(e)}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                "lead_data": None,
                "thread_id": thread_id,
                "success": False,
                "error": str(e)
            }
    
    async def _simulate_agent_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Simulate agent response for demo. Replace with actual AgenticMCP integration."""
        
        # Load system prompt from file
        system_prompt = self._load_system_prompt()
        
        # Simple keyword-based responses for demo
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["engagement", "ring", "proposal", "diamond"]):
            return """I'd be delighted to help you find the perfect engagement ring! At Brax Fine Jewelers, we specialize in creating unforgettable moments with our exquisite diamond collection.

Our engagement rings feature:
- Certified diamonds with exceptional clarity and brilliance
- Custom design services to create your unique vision
- Expert guidance on the 4 C's (Cut, Color, Clarity, Carat)
- Lifetime warranty and complimentary maintenance

I'd love to learn more about what you're looking for. What's your budget range, and do you have any specific style preferences?

```lead
{
  "name": "",
  "email": "",
  "phone": "",
  "intent": "engagement_ring",
  "notes": "Interested in engagement rings, needs consultation on budget and style preferences"
}
```"""
        
        elif any(word in message_lower for word in ["repair", "fix", "broken", "maintenance"]):
            return """I can certainly help you with jewelry repair services! Brax Fine Jewelers offers comprehensive repair and maintenance services to keep your precious pieces looking their best.

Our repair services include:
- Ring resizing and reshaping
- Stone replacement and setting repair
- Chain and clasp repair
- Cleaning and polishing
- Antique jewelry restoration

To provide you with an accurate estimate, I'd recommend bringing your piece in for a free evaluation. Would you like me to schedule an appointment for you?

```lead
{
  "name": "",
  "email": "",
  "phone": "",
  "intent": "jewelry_repair",
  "notes": "Needs jewelry repair services, interested in free evaluation appointment"
}
```"""
        
        elif any(word in message_lower for word in ["watch", "timepiece", "rolex", "omega"]):
            return """Welcome to our luxury timepiece collection! Brax Fine Jewelers is an authorized dealer for premier watch brands including Rolex, Omega, TAG Heuer, and more.

Whether you're looking for:
- Classic dress watches for professional settings
- Sports watches with advanced complications
- Vintage or limited edition pieces
- Investment-grade timepieces

Our certified watch specialists can guide you through our collection and help you find the perfect timepiece. Are you looking for a specific brand or style?

```lead
{
  "name": "",
  "email": "",
  "phone": "",
  "intent": "luxury_watches",
  "notes": "Interested in luxury timepieces, needs consultation with watch specialist"
}
```"""
        
        else:
            return f"""Thank you for reaching out to Brax Fine Jewelers! I'm here to help you with all your fine jewelry needs.

{system_prompt}

How can I assist you today? Whether you're looking for engagement rings, luxury watches, custom jewelry design, or repair services, I'm here to provide expert guidance."""
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from prompts/system_prompt.md"""
        try:
            with open("backend/prompts/system_prompt.md", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "I'm your dedicated jewelry concierge at Brax Fine Jewelers, here to help you find the perfect piece or answer any questions about our collection."
    
    def _extract_lead_data(self, response: str) -> Dict[str, Any] | None:
        """Extract lead data from response if present in ```lead blocks."""
        pattern = r"```lead\s*\n(.*?)\n```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            try:
                lead_json = match.group(1).strip()
                return json.loads(lead_json)
            except json.JSONDecodeError:
                log.warning("Failed to parse lead JSON from response")
        return None