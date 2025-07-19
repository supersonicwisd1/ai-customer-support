import warnings
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

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
from app.api.chat import router as chat_router
from app.api.search import router as search_router
from app.api.voice import router as voice_router
from app.api.guardrails import router as guardrails_router

# Set up logging
# logging.basicConfig(level=logging.INFO) # This line is now redundant as logging is configured globally
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aven AI",
    description="Aven AI is a platform for AI-powered search and retrieval of information.",
    version="0.1.0",
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(chat_router)
app.include_router(search_router)
app.include_router(voice_router)
app.include_router(guardrails_router)

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Aven AI Customer care support"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# WebSocket endpoint for real-time chat
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # For now, just echo back
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
