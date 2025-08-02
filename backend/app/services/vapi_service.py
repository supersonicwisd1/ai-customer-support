import os
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from vapi import Vapi
from dotenv import load_dotenv
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class VapiService:
    """VAPI service for real-time voice interactions"""
    
    def __init__(self):
        self.vapi_token = os.getenv("VAPI_PRIVATE_KEY")
        if not self.vapi_token:
            raise ValueError("VAPI_PRIVATE_KEY environment variable is not set")
        
        self.vapi = Vapi(token=self.vapi_token)
        self.assistant_id = None
        self._setup_assistant()
        self.openai_service = OpenAIService()
        self.pinecone_service = PineconeService()
    
    def _setup_assistant(self):
        """Create or get the Aven AI assistant"""
        try:
            # Try to find existing assistant
            assistants = self.vapi.assistants.list()
            for assistant in assistants:
                if assistant.name == "Aven AI Customer Care":
                    self.assistant_id = assistant.id
                    logger.info(f"Using existing assistant: {self.assistant_id}")
                    return
            
            # Create new assistant if not found
            logger.info("Creating new Aven AI assistant...")
            assistant = self.vapi.assistants.create(
                name="Aven AI Customer Care",
                first_message="Hello! I'm your Aven AI assistant. How can I help you today?",
                model={
                    "provider": "openai",
                    "model": "gpt-4o",
                    "temperature": 0.7,
                    "messages": [{
                        "role": "system",
                        "content": """You are Aven AI's customer care assistant. You help customers with:

1. **Credit Card Information**: Explain Aven's credit card features, benefits, and application process
2. **Account Support**: Help with account management, login issues, and general inquiries
3. **Product Information**: Provide details about Aven's financial technology solutions
4. **General Support**: Answer questions about Aven's services and company information

Contact Information:
- Email: support@aven.com
- Support Website: https://www.aven.com/support

Key Guidelines:
- Be friendly, professional, and helpful
- Keep responses concise but informative
- If you don't have specific information, suggest contacting Aven's support team
- Focus on Aven-related topics and financial technology
- Use a conversational, natural tone
- Always provide the correct contact information when needed

Remember: You're representing Aven AI, a financial technology company."""
                    }]
                },
                voice={
                    "provider": "11labs",
                    "voice_id": "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
                }
            )
            
            self.assistant_id = assistant.id
            logger.info(f"Created new assistant: {self.assistant_id}")
            
        except Exception as e:
            logger.error(f"Error setting up VAPI assistant: {e}")
            raise
    
    async def create_web_call(self, session_id: str) -> Dict[str, Any]:
        """Create a web-based voice call for real-time conversation"""
        try:
            # Create a web call using VAPI
            call = self.vapi.calls.create(
                assistant_id=self.assistant_id,
                metadata={
                    "session_id": session_id,
                    "call_type": "web",
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Created VAPI web call: {call.id} for session: {session_id}")
            
            return {
                "call_id": call.id,
                "status": call.status,
                "session_id": session_id,
                "assistant_id": self.assistant_id
            }
            
        except Exception as e:
            logger.error(f"Error creating VAPI web call: {e}")
            raise
    
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Get the current status of a call"""
        try:
            call = self.vapi.calls.get(call_id)
            return {
                "call_id": call.id,
                "status": call.status,
                "duration": call.duration,
                "metadata": call.metadata
            }
        except Exception as e:
            logger.error(f"Error getting call status: {e}")
            raise
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End an active call"""
        try:
            call = self.vapi.calls.update(call_id, status="ended")
            logger.info(f"Ended call: {call_id}")
            return {
                "call_id": call.id,
                "status": call.status,
                "duration": call.duration
            }
        except Exception as e:
            logger.error(f"Error ending call: {e}")
            raise
    
    async def list_calls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent calls"""
        try:
            calls = self.vapi.calls.list(limit=limit)
            return [
                {
                    "call_id": call.id,
                    "status": call.status,
                    "duration": call.duration,
                    "metadata": call.metadata,
                    "created_at": call.created_at
                }
                for call in calls
            ]
        except Exception as e:
            logger.error(f"Error listing calls: {e}")
            raise
    
    def get_web_sdk_config(self) -> Dict[str, Any]:
        """Get configuration for the VAPI Web SDK"""
        return {
            "api_key": os.getenv("VAPI_PUBLIC_KEY"),
            "assistant_id": self.assistant_id,
            "config": {
                "button": {
                    "color": "#12A594",
                    "text": "Talk to Aven AI",
                    "icon": "🎤"
                },
                "widget": {
                    "position": "bottom-right",
                    "theme": "light"
                }
            }
        }

    async def get_knowledge_based_response(self, query: str) -> dict:
        """Answer a query using the enhanced intelligent response system."""
        try:
            # Use the enhanced assistant service for better responses
            from app.services.assistant_service import AssistantService
            assistant_service = AssistantService()
            
            # Process the query with enhanced intelligence
            response = await assistant_service.process_message(query)
            
            return {
                "answer": response.get("answer", ""),
                "sources": response.get("sources", []),
                "context": response.get("context_used", ""),
                "confidence": response.get("confidence", 0.0),
                "response_type": response.get("response_type", "general"),
                "suggestions": response.get("suggestions", [])
            }
        except Exception as e:
            logging.error(f"VapiService knowledge base Q&A error: {e}")
            return {
                "answer": "I apologize, but I'm having trouble processing your request right now. Please try again or contact Aven's customer support for immediate assistance.",
                "error": str(e)
            }