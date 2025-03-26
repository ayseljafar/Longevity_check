from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import os
from dotenv import load_dotenv


load_dotenv()

# Import our custom modules
from .session_manager import SessionManager
from .llm_orchestrator import LLMOrchestrator
from .knowledge_base import KnowledgeBase

app = FastAPI(title="Longevity Agent API")

# Initialize our components
session_manager = SessionManager()
knowledge_base = KnowledgeBase()
llm_orchestrator = LLMOrchestrator(knowledge_base)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    recommendations: Optional[Dict[str, Any]] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a user message and return an AI response with recommendations.
    
    Parameters:
    - session_id: Unique identifier for the user session
    - message: User's input message
    - metadata: Optional additional information about the request
    
    Returns:
    - session_id: Same session_id as provided in the request
    - response: AI-generated response text
    - recommendations: Optional structured data with supplement recommendations, if any
    """
    try:
        # Get or create session context
        session_context = session_manager.get_session(request.session_id)
        
        # Add the new user message to the session context
        session_context["messages"].append({"role": "user", "content": request.message})
        
        # Process message with LLM orchestrator
        response, recommendations = llm_orchestrator.process_message(
            user_message=request.message,
            session_context=session_context
        )
        
        # Update session with assistant response
        session_context["messages"].append({"role": "assistant", "content": response})
        
        # If there are recommendations, add them to the session
        if recommendations:
            if "recommendations" not in session_context:
                session_context["recommendations"] = []
            session_context["recommendations"].append(recommendations)
        
        # Save updated session
        session_manager.update_session(request.session_id, session_context)
        
        return ChatResponse(
            session_id=request.session_id,
            response=response,
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(app, host="0.0.0.0", port=8000)
