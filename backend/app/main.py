import warnings
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime

# Configure logging and suppress warnings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress Pydantic field name warnings
warnings.filterwarnings("ignore", message="Field name.*shadows an attribute in parent.*")
warnings.filterwarnings("ignore", message="Field name.*shadows an attribute in parent.*BaseModel.*")
warnings.filterwarnings("ignore", message="Field name.*shadows an attribute in parent.*FirecrawlDocument.*")

# Suppress specific library warnings
logging.getLogger("pydantic").setLevel(logging.ERROR)
logging.getLogger("firecrawl").setLevel(logging.WARNING)

from app.config import settings

# Import API routes
from app.api import guardrails, cache, vapi, chat, knowledge

# Set up logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aven AI Support Backend",
    description="AI-powered customer support system for Aven",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only include necessary routers
app.include_router(guardrails.router, prefix="/api")
app.include_router(cache.router, prefix="/api")
app.include_router(vapi.router)
app.include_router(chat.router)
app.include_router(knowledge.router)

@app.get("/")
async def root():
    return {"message": "Aven AI Support Backend API"}

@app.get("/health")
async def health_check():
    """Basic health check that doesn't require API keys"""
    return {
        "status": "ok", 
        "message": "Backend is running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check that tests all services (requires API keys)"""
    health_status = {
        "status": "ok",
        "services": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Test VAPI service
    try:
        from app.api.vapi import get_vapi_service
        vapi_service = get_vapi_service()
        config = vapi_service.get_web_sdk_config()
        health_status["services"]["vapi"] = "healthy"
    except Exception as e:
        health_status["services"]["vapi"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Test guardrails service
    try:
        from app.api.guardrails import get_guardrails_service
        guardrails_service = get_guardrails_service()
        # Test with a simple safe text
        result = guardrails_service.check_text("Hello")
        health_status["services"]["guardrails"] = "healthy"
    except Exception as e:
        health_status["services"]["guardrails"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
