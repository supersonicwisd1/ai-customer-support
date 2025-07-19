from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.guardrails import GuardrailsService, SafetyLevel

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/guardrails", tags=["guardrails"])

# Global guardrails service
_guardrails_service: Optional[GuardrailsService] = None

def get_guardrails_service() -> GuardrailsService:
    """Get or create guardrails service instance"""
    global _guardrails_service
    if _guardrails_service is None:
        _guardrails_service = GuardrailsService()
    return _guardrails_service

def get_user_id(request: Request) -> str:
    """Extract user ID from request (simplified - in production, use proper auth)"""
    # In a real implementation, this would extract from JWT token or session
    user_agent = request.headers.get("user-agent", "unknown")
    client_ip = request.client.host if request.client else "unknown"
    return f"{client_ip}_{user_agent[:50]}"

@router.post("/check-input")
async def check_user_input(
    request: Request,
    message: str,
    guardrails: GuardrailsService = Depends(get_guardrails_service)
):
    """Check user input for safety and appropriateness"""
    try:
        user_id = get_user_id(request)
        
        # Perform safety check
        safety_check = guardrails.check_user_input(user_id, message)
        
        return {
            "safe": safety_check.level == SafetyLevel.SAFE,
            "level": safety_check.level.value,
            "reason": safety_check.reason,
            "details": safety_check.details,
            "timestamp": safety_check.timestamp.isoformat(),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error checking user input: {str(e)}")
        raise HTTPException(status_code=500, detail="Safety check failed")

@router.post("/check-response")
async def check_ai_response(
    request: Request,
    response: str,
    original_query: str,
    guardrails: GuardrailsService = Depends(get_guardrails_service)
):
    """Check AI response for safety and appropriateness"""
    try:
        user_id = get_user_id(request)
        
        # Perform safety check
        safety_check = guardrails.check_ai_response(response, user_id, original_query)
        
        return {
            "safe": safety_check.level == SafetyLevel.SAFE,
            "level": safety_check.level.value,
            "reason": safety_check.reason,
            "details": safety_check.details,
            "timestamp": safety_check.timestamp.isoformat(),
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error checking AI response: {str(e)}")
        raise HTTPException(status_code=500, detail="Response safety check failed")

@router.get("/stats")
async def get_safety_stats(
    guardrails: GuardrailsService = Depends(get_guardrails_service)
):
    """Get safety statistics"""
    try:
        stats = guardrails.get_safety_stats()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting safety stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get safety statistics")

@router.get("/export-log")
async def export_safety_log(
    guardrails: GuardrailsService = Depends(get_guardrails_service)
):
    """Export safety log for analysis"""
    try:
        log_data = guardrails.export_safety_log()
        return JSONResponse(
            content=log_data,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=safety_log.json"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting safety log: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export safety log")

@router.post("/block-user")
async def block_user(
    user_id: str,
    reason: str = "Manual block",
    guardrails: GuardrailsService = Depends(get_guardrails_service)
):
    """Block a user from using the service"""
    try:
        guardrails.block_user(user_id, reason)
        return {
            "success": True,
            "message": f"User {user_id} blocked successfully",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error blocking user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to block user")

@router.post("/unblock-user")
async def unblock_user(
    user_id: str,
    guardrails: GuardrailsService = Depends(get_guardrails_service)
):
    """Unblock a user"""
    try:
        guardrails.unblock_user(user_id)
        return {
            "success": True,
            "message": f"User {user_id} unblocked successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error unblocking user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unblock user")

@router.get("/health")
async def guardrails_health(
    guardrails: GuardrailsService = Depends(get_guardrails_service)
):
    """Health check for guardrails service"""
    try:
        stats = guardrails.get_safety_stats()
        return {
            "status": "healthy",
            "service": "guardrails",
            "timestamp": datetime.utcnow().isoformat(),
            "active_users": len(guardrails.user_requests),
            "blocked_users": len(guardrails.blocked_users),
            "total_requests": stats["total_requests"]
        }
        
    except Exception as e:
        logger.error(f"Guardrails health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "guardrails",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 