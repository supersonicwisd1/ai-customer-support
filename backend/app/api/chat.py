from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime
from pydantic import BaseModel

from ..services.assistant_service import AssistantService
from ..services.guardrails_service import GuardrailsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Lazy initialization - only create when needed
_assistant_service = None
_guardrails_service = None

def get_assistant_service():
    global _assistant_service
    if _assistant_service is None:
        _assistant_service = AssistantService()
    return _assistant_service

def get_guardrails_service():
    global _guardrails_service
    if _guardrails_service is None:
        _guardrails_service = GuardrailsService()
    return _guardrails_service

class ChatMessage(BaseModel):
    message: str

@router.post("/message")
async def send_message(chat_message: ChatMessage) -> Dict[str, Any]:
    """Send a text message and get AI response with guardrail checks"""
    try:
        # 1. Guardrail check on user input
        guardrails_service = get_guardrails_service()
        guardrail_result = guardrails_service.check_text(chat_message.message)
        
        if guardrail_result["status"] != "safe":
            logger.warning(f"Message blocked by guardrails: {guardrail_result}")
            return {
                "success": False,
                "error": "Message blocked by safety checks",
                "reason": guardrail_result["reason"],
                "categories": guardrail_result["categories"],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # 2. Process message with assistant service
        assistant_service = get_assistant_service()
        response = await assistant_service.process_message(chat_message.message)
        
        # 3. Guardrail check on AI response (optional - for extra safety)
        response_guardrail = guardrails_service.check_text(response.get("message", ""))
        if response_guardrail["status"] != "safe":
            logger.warning(f"AI response flagged by guardrails: {response_guardrail}")
            # Return a safe fallback response
            response = {
                "message": "I apologize, but I cannot provide that information. Please ask a different question about Aven's services.",
                "sources": [],
                "confidence": 0.0
            }
        
        return {
            "success": True,
            "response": response,
            "guardrails": {
                "input_checked": True,
                "response_checked": True,
                "input_status": guardrail_result["status"],
                "response_status": response_guardrail["status"]
            },
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
        guardrails_service = get_guardrails_service()
        
        # Test guardrails
        test_message = "Hello"
        guardrail_result = guardrails_service.check_text(test_message)
        
        # Test with a simple message
        response = await assistant_service.process_message("Hello")
        
        return {
            "success": True,
            "status": "healthy",
            "guardrails_status": guardrail_result["status"],
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