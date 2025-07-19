from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import Response
import logging
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from app.services.voice_service import VoiceService
from app.core.ai_agent import AIAgent
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.models.chat import ChatRequest

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/voice", tags=["voice"])

# Global services
_voice_service: Optional[VoiceService] = None
_ai_agent: Optional[AIAgent] = None

def get_voice_service() -> VoiceService:
    """Get or create voice service instance"""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service

def get_ai_agent() -> AIAgent:
    """Get or create AI agent instance"""
    global _ai_agent
    if _ai_agent is None:
        try:
            openai_service = OpenAIService()
            pinecone_service = PineconeService()
            pinecone_service.initialize_index()
            _ai_agent = AIAgent(openai_service, pinecone_service)
        except Exception as e:
            logger.error(f"Failed to initialize AI Agent: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize AI Agent")
    return _ai_agent

@router.post("/chat")
async def voice_chat(
    audio_file: UploadFile = File(...),
    session_id: Optional[str] = None,
    voice_service: VoiceService = Depends(get_voice_service),
    ai_agent: AIAgent = Depends(get_ai_agent)
):
    """Process voice chat: transcribe → chat → synthesize"""
    try:
        # Validate voice service
        if not voice_service.is_available():
            raise HTTPException(status_code=503, detail="Voice service not configured")
        
        # Validate audio file
        if not audio_file.filename or not audio_file.filename.lower().endswith(('.wav', '.mp3', '.m4a')):
            raise HTTPException(status_code=400, detail="Invalid audio file format. Supported: WAV, MP3, M4A")
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        logger.info(f"Processing voice chat for session: {session_id}")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Step 1: Transcribe audio to text
        transcription = await voice_service.transcribe_audio(audio_data)
        
        if not transcription.strip():
            return {
                "error": "No speech detected in audio",
                "transcription": "",
                "response": "",
                "session_id": session_id
            }
        
        # Step 2: Process with AI agent
        chat_request = ChatRequest(
            message=transcription,
            session_id=session_id,
            include_sources=True
        )
        
        chat_response = await ai_agent.process_chat(chat_request)
        
        # Step 3: Convert response to speech
        audio_response = await voice_service.text_to_speech(chat_response.message)
        
        # Return response with audio
        return {
            "transcription": transcription,
            "response": chat_response.message,
            "session_id": session_id,
            "confidence": chat_response.confidence,
            "sources": chat_response.sources,
            "audio_url": f"/api/voice/audio/{session_id}"  # Endpoint to get audio
        }
        
    except Exception as e:
        logger.error(f"Error in voice chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice chat failed: {str(e)}")

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    voice_service: VoiceService = Depends(get_voice_service)
):
    """Transcribe audio to text only"""
    try:
        if not voice_service.is_available():
            raise HTTPException(status_code=503, detail="Voice service not configured")
        
        # Validate audio file
        if not audio_file.filename or not audio_file.filename.lower().endswith(('.wav', '.mp3', '.m4a')):
            raise HTTPException(status_code=400, detail="Invalid audio file format")
        
        # Read and transcribe audio
        audio_data = await audio_file.read()
        transcription = await voice_service.transcribe_audio(audio_data)
        
        return {
            "transcription": transcription,
            "confidence": 1.0 if transcription.strip() else 0.0
        }
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/synthesize")
async def synthesize_speech(
    text: str,
    voice: str = "alloy",
    voice_service: VoiceService = Depends(get_voice_service)
):
    """Convert text to speech"""
    try:
        if not voice_service.is_available():
            raise HTTPException(status_code=503, detail="Voice service not configured")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Convert text to speech
        audio_data = await voice_service.text_to_speech(text, voice)
        
        # Return audio file
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )
        
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@router.get("/voices")
async def get_voices(voice_service: VoiceService = Depends(get_voice_service)):
    """Get available voices and voice service info"""
    try:
        voice_info = await voice_service.get_voice_info()
        return voice_info
        
    except Exception as e:
        logger.error(f"Error getting voice info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get voice information")

@router.get("/health")
async def voice_health(voice_service: VoiceService = Depends(get_voice_service)):
    """Health check for voice service"""
    return {
        "status": "healthy" if voice_service.is_available() else "unavailable",
        "available": voice_service.is_available(),
        "service": "voice",
        "timestamp": datetime.utcnow()
    } 