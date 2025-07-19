import logging
import asyncio
import base64
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
import httpx
from app.models.chat import ChatRequest, ChatResponse
import os

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for voice chat using OpenAI Realtime API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/audio"
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set - voice service will be disabled")
    
    async def transcribe_audio(self, audio_data: bytes, format: str = "wav") -> str:
        """Transcribe audio to text using OpenAI Whisper"""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            url = f"{self.base_url}/transcriptions"
            
            files = {
                "file": ("audio.wav", audio_data, "audio/wav")
            }
            
            data = {
                "model": "whisper-1",
                "response_format": "text"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, files=files, data=data, headers=headers)
                response.raise_for_status()
                
                transcription = response.text
                logger.info(f"Audio transcribed successfully: {len(transcription)} characters")
                return transcription
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
    
    async def text_to_speech(self, text: str, voice: str = "alloy") -> bytes:
        """Convert text to speech using OpenAI TTS"""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            url = f"{self.base_url}/speech"
            
            data = {
                "model": "tts-1",
                "input": text,
                "voice": voice,
                "response_format": "mp3",
                "speed": 1.0
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                
                audio_data = response.content
                logger.info(f"Text converted to speech: {len(audio_data)} bytes")
                return audio_data
                
        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            raise
    
    async def process_voice_chat(self, audio_data: bytes, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process voice chat: transcribe → chat → synthesize"""
        try:
            # Step 1: Transcribe audio to text
            logger.info("Transcribing audio to text...")
            transcription = await self.transcribe_audio(audio_data)
            
            if not transcription.strip():
                return {
                    "error": "No speech detected in audio",
                    "transcription": "",
                    "response": "",
                    "audio_response": None
                }
            
            # Step 2: Process with chat (this will be handled by the AI agent)
            logger.info(f"Transcription: {transcription}")
            
            # Step 3: Convert response to speech (placeholder - will be implemented)
            # For now, return the transcription and a placeholder response
            return {
                "transcription": transcription,
                "response": f"I heard you say: {transcription}. This is a placeholder response for voice chat.",
                "audio_response": None,  # Will be implemented
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error in voice chat processing: {str(e)}")
            return {
                "error": f"Voice processing failed: {str(e)}",
                "transcription": "",
                "response": "",
                "audio_response": None
            }
    
    def is_available(self) -> bool:
        """Check if voice service is properly configured"""
        return bool(self.api_key)
    
    async def get_supported_voices(self) -> List[str]:
        """Get list of supported TTS voices"""
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    async def get_voice_info(self) -> Dict[str, Any]:
        """Get voice service information"""
        return {
            "available": self.is_available(),
            "supported_voices": await self.get_supported_voices(),
            "features": {
                "speech_to_text": True,
                "text_to_speech": True,
                "real_time": False  # Will be True when we implement streaming
            }
        } 