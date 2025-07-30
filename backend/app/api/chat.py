from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime
from pydantic import BaseModel

from ..services.assistant_service import AssistantService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Lazy initialization - only create when needed
_assistant_service = None

def get_assistant_service():
    global _assistant_service
    if _assistant_service is None:
        _assistant_service = AssistantService()
    return _assistant_service

class ChatMessage(BaseModel):
    message: str

@router.post("/message")
async def send_message(chat_message: ChatMessage) -> Dict[str, Any]:
    """Send a text message and get AI response"""
    try:
        assistant_service = get_assistant_service()
        response = await assistant_service.process_message(chat_message.message)
        
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/health")
async def chat_health_check() -> Dict[str, Any]:
    """Health check for chat service"""
    try:
        assistant_service = get_assistant_service()
        # Test with a simple message
        response = await assistant_service.process_message("Hello")
        return {
            "success": True,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Chat service health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 