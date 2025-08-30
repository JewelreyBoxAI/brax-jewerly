import asyncio, logging, json, uuid, re
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from ..config.settings import settings
from ..db.database import SessionLocal, engine
from ..db.models import Base, Thread, Message, Lead
from ..services.ghl import forward_lead_webhook, upsert_contact_rest
from ..services.redis_cache import cache_get, cache_setex
from ..core.build_graph import create_brax_chat_graph
from ..core.state import AgentState
from langchain_core.messages import HumanMessage, AIMessage

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("brax_api")

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize the conversation graph
chat_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chat_graph
    log.info("Initializing Brax Chat Graph...")
    chat_graph = create_brax_chat_graph()
    log.info("Chat graph initialized successfully")
    yield
    log.info("Shutting down...")

app = FastAPI(
    title="Brax AI Concierge API",
    description="HTTP chatbot API for Brax Fine Jewelers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    thread_id: str | None = None
    user_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str
    message_id: int
    timestamp: datetime
    lead_captured: bool = False

class ThreadHistory(BaseModel):
    thread_id: str
    messages: List[Dict[str, Any]]

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "brax-chat-api"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage, db: Session = Depends(get_db)):
    """Main chat endpoint."""
    try:
        # Generate thread ID if not provided
        thread_id = message.thread_id or str(uuid.uuid4())
        user_id = message.user_id or "anonymous"
        
        # Ensure thread exists
        thread = db.query(Thread).filter(Thread.id == thread_id).first()
        if not thread:
            thread = Thread(id=thread_id, user_id=user_id)
            db.add(thread)
            db.commit()
        
        # Save user message
        user_msg = Message(
            thread_id=thread_id,
            role="user",
            content=message.message
        )
        db.add(user_msg)
        db.commit()
        
        # Get conversation history
        messages = db.query(Message).filter(Message.thread_id == thread_id).order_by(Message.created_at).all()
        
        # Convert to LangChain format
        lc_messages = []
        for msg in messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))
        
        # Process through the graph
        state = AgentState(
            messages=lc_messages,
            user_id=user_id,
            thread_id=thread_id
        )
        
        result = await chat_graph.ainvoke(state)
        
        # Get the AI response
        ai_response = result["messages"][-1].content
        
        # Save AI response
        ai_msg = Message(
            thread_id=thread_id,
            role="assistant", 
            content=ai_response
        )
        db.add(ai_msg)
        db.commit()
        
        # Check for lead data and process
        lead_captured = await process_lead_capture(ai_response, thread_id, db)
        
        return ChatResponse(
            response=ai_response,
            thread_id=thread_id,
            message_id=ai_msg.id,
            timestamp=ai_msg.created_at,
            lead_captured=lead_captured
        )
        
    except Exception as e:
        log.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/thread/{thread_id}/history", response_model=ThreadHistory)
async def get_thread_history(thread_id: str, db: Session = Depends(get_db)):
    """Get conversation history for a thread."""
    try:
        messages = db.query(Message).filter(Message.thread_id == thread_id).order_by(Message.created_at).all()
        
        return ThreadHistory(
            thread_id=thread_id,
            messages=[
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        )
        
    except Exception as e:
        log.error(f"History endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_lead_capture(response: str, thread_id: str, db: Session) -> bool:
    """Extract and process lead data from agent response."""
    try:
        # Extract lead JSON from response
        pattern = r"```lead\s*\n(.*?)\n```"
        match = re.search(pattern, response, re.DOTALL)
        
        if not match:
            return False
        
        lead_json = match.group(1).strip()
        lead_data = json.loads(lead_json)
        
        # Save to database
        lead = Lead(
            thread_id=thread_id,
            name=lead_data.get("name"),
            email=lead_data.get("email"), 
            phone=lead_data.get("phone"),
            intent=lead_data.get("intent"),
            notes=lead_data.get("notes"),
            raw=json.dumps(lead_data)
        )
        db.add(lead)
        db.commit()
        
        # Forward to GHL
        asyncio.create_task(forward_to_ghl(lead_data, thread_id))
        
        return True
        
    except Exception as e:
        log.error(f"Lead capture error: {str(e)}")
        return False

async def forward_to_ghl(lead_data: Dict[str, Any], thread_id: str):
    """Forward lead to GoHighLevel."""
    try:
        # Add metadata
        enhanced_lead = {
            **lead_data,
            "source": "Brax AI Concierge",
            "thread_id": thread_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Try webhook first
        webhook_result = await forward_lead_webhook(enhanced_lead)
        log.info(f"Webhook result: {webhook_result}")
        
        # Try REST API if configured
        if settings.ghl_api_key:
            rest_result = await upsert_contact_rest(enhanced_lead)
            log.info(f"REST result: {rest_result}")
            
    except Exception as e:
        log.error(f"GHL forwarding error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)