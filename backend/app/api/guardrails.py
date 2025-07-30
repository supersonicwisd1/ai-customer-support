from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from app.services.guardrails_service import GuardrailsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/guardrails", tags=["guardrails"])

# Lazy initialization - only create when needed
_guardrails_service = None

def get_guardrails_service():
    global _guardrails_service
    if _guardrails_service is None:
        _guardrails_service = GuardrailsService()
    return _guardrails_service

@router.post("/check")
async def check_text_guardrails(text: str) -> Dict[str, Any]:
    """Check text for safety and compliance using GuardrailsService (OpenAI Moderation)."""
    try:
        guardrails_service = get_guardrails_service()
        result = guardrails_service.check_text(text)
        return result
    except Exception as e:
        logger.error(f"Guardrails check error: {e}")
        raise HTTPException(status_code=500, detail="Guardrails check failed") 