from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

from app.models.chat import ChatRequest, ChatResponse, ChatSession
from app.core.ai_agent import AIAgent
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.services.search_service import SearchService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/chat", tags=["chat"])

# Global AI agent instance (in production, use dependency injection)
_ai_agent: Optional[AIAgent] = None

def get_ai_agent() -> AIAgent:
    """Get or create AI agent instance"""
    global _ai_agent
    if _ai_agent is None:
        try:
            # Ensure environment variables are loaded
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY not found in environment")
            if not os.getenv("PINECONE_API_KEY"):
                raise ValueError("PINECONE_API_KEY not found in environment")
            
            openai_service = OpenAIService()
            pinecone_service = PineconeService()
            pinecone_service.initialize_index()
            
            _ai_agent = AIAgent(openai_service, pinecone_service)
            logger.info("AI Agent initialized successfully with search service")
        except Exception as e:
            logger.error(f"Failed to initialize AI Agent: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize AI Agent: {str(e)}")
    return _ai_agent

@router.post("/text", response_model=ChatResponse)
async def chat_text(request: ChatRequest, ai_agent: AIAgent = Depends(get_ai_agent)):
    """Handle text chat requests"""
    try:
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
        
        logger.info(f"Processing chat request: {request.message[:50]}...")
        
        # Process the chat request
        response = await ai_agent.process_chat(request)
        
        logger.info(f"Chat response generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, ai_agent: AIAgent = Depends(get_ai_agent)):
    """Get chat history for a session"""
    try:
        history = await ai_agent.get_chat_history(session_id)
        return {
            "session_id": session_id,
            "history": history,
            "message_count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")

@router.delete("/session/{session_id}")
async def clear_chat_session(session_id: str, ai_agent: AIAgent = Depends(get_ai_agent)):
    """Clear a chat session"""
    try:
        success = await ai_agent.clear_session(session_id)
        if success:
            return {"message": "Session cleared successfully", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear session")

@router.get("/health")
async def chat_health():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "chat"
    } 