from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
import logging
from datetime import datetime

from ..services.vapi_service import VapiService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vapi", tags=["vapi"])

# Lazy initialization - only create when needed
_vapi_service = None

def get_vapi_service():
    global _vapi_service
    if _vapi_service is None:
        _vapi_service = VapiService()
    return _vapi_service

@router.get("/config")
async def get_vapi_config() -> Dict[str, Any]:
    """Get VAPI configuration for frontend integration"""
    try:
        vapi_service = get_vapi_service()
        config = vapi_service.get_web_sdk_config()
        return {
            "success": True,
            "config": config,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting VAPI config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get VAPI config: {str(e)}")

@router.post("/calls")
async def create_call(session_id: str) -> Dict[str, Any]:
    """Create a new VAPI web call"""
    try:
        vapi_service = get_vapi_service()
        call_data = await vapi_service.create_web_call(session_id)
        return {
            "success": True,
            "call": call_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating VAPI call: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create call: {str(e)}")

@router.get("/calls/{call_id}")
async def get_call_status(call_id: str) -> Dict[str, Any]:
    """Get the status of a specific call"""
    try:
        vapi_service = get_vapi_service()
        call_data = await vapi_service.get_call_status(call_id)
        return {
            "success": True,
            "call": call_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting call status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get call status: {str(e)}")

@router.put("/calls/{call_id}/end")
async def end_call(call_id: str) -> Dict[str, Any]:
    """End a specific call"""
    try:
        vapi_service = get_vapi_service()
        call_data = await vapi_service.end_call(call_id)
        return {
            "success": True,
            "call": call_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end call: {str(e)}")

@router.get("/calls")
async def list_calls(limit: int = 10) -> Dict[str, Any]:
    """List recent calls"""
    try:
        vapi_service = get_vapi_service()
        calls = await vapi_service.list_calls(limit)
        return {
            "success": True,
            "calls": calls,
            "count": len(calls),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error listing calls: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list calls: {str(e)}")

@router.post("/webhook")
async def vapi_webhook(request: Request):
    """VAPI fulfillment webhook: receives a query, returns a knowledge-based answer."""
    try:
        vapi_service = get_vapi_service()
        data = await request.json()
        query = data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Missing 'query' in request body")
        result = await vapi_service.get_knowledge_based_response(query)
        return {"success": True, "result": result, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"VAPI webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"VAPI webhook error: {str(e)}")

@router.get("/health")
async def vapi_health_check() -> Dict[str, Any]:
    """Health check for VAPI service"""
    try:
        vapi_service = get_vapi_service()
        # Test VAPI connection by getting config
        config = vapi_service.get_web_sdk_config()
        return {
            "status": "healthy",
            "vapi_connected": True,
            "assistant_id": vapi_service.assistant_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"VAPI health check failed: {e}")
        return {
            "status": "unhealthy",
            "vapi_connected": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }