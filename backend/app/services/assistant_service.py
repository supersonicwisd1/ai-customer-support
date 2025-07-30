import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.services.cache_service import CacheService
from app.services.guardrails_service import GuardrailsService
from app.services.query_analyzer import QueryAnalyzer
from app.services.calendar_service import CalendarService
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class AssistantService:
    """Orchestrates text and voice Q&A for the AI customer care assistant, with calendar and NLP integration."""
    def __init__(self):
        self.openai_service = OpenAIService()
        self.pinecone_service = PineconeService()
        self.cache_service = CacheService()
        self.guardrails_service = GuardrailsService()
        self.query_analyzer = QueryAnalyzer()
        self.calendar_service = CalendarService()
        self.session_history: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> list of messages

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a text message and return AI response - simplified for chat interface"""
        try:
            # Step 1: Analyze query
            analysis = self.query_analyzer.analyze_query(message)
            logger.info(f"Query analysis: {analysis}")

            # Step 2: Calendar trigger
            if analysis.get("calendar_trigger"):
                meeting = await self.calendar_service.schedule_meeting("user")
                answer = f"A meeting has been scheduled for you. Details: {meeting}"
                return {
                    "answer": answer,
                    "calendar": meeting,
                    "analysis": analysis,
                    "guardrails": {"status": "safe"}
                }

            # Step 3: Embed question
            embedding = await self.openai_service.generate_embeddings(message)
            # Step 4: Search Pinecone
            kb_results = await self.pinecone_service.search_similar(embedding, top_k=5)
            
            if not kb_results:
                logger.warning("No results found in Pinecone, using fallback response")
                answer = "I'm sorry, I don't have specific information about that in my knowledge base. Please try asking about Aven's services, credit cards, or general information, or contact Aven's customer support directly."
                return {
                    "answer": answer,
                    "sources": [],
                    "context": "",
                    "guardrails": {"status": "safe"},
                    "analysis": analysis
                }
            
            context = "\n\n".join([r["text"] for r in kb_results if r.get("text")])
            sources = [{"url": r["url"], "score": r["score"]} for r in kb_results]
            # Step 5: Generate answer with OpenAI
            answer = await self.openai_service.generate_response(message, context)
            # Step 6: Guardrails check
            guardrails_result = self.guardrails_service.check_text(answer)
            if guardrails_result["status"] != "safe":
                logger.warning(f"Guardrails triggered: {guardrails_result}")
                fallback = "Sorry, I can't answer that question."
                return {
                    "answer": fallback,
                    "sources": sources,
                    "context": context,
                    "guardrails": guardrails_result,
                    "analysis": analysis
                }
            # If safe, return answer
            return {
                "answer": answer,
                "sources": sources,
                "context": context,
                "guardrails": guardrails_result,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"AssistantService process_message error: {e}")
            return {"error": str(e)}

    async def answer_text_question(self, question: str, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Answer a text question using KB search, OpenAI, NLP, and calendar integration. Guardrails enforced."""
        try:
            # Maintain chat history
            if session_id not in self.session_history:
                self.session_history[session_id] = []
            self.session_history[session_id].append({"role": "user", "content": question})

            # Step 1: Analyze query
            analysis = self.query_analyzer.analyze_query(question)
            logger.info(f"Query analysis: {analysis}")

            # Step 2: Calendar trigger
            if analysis.get("calendar_trigger"):
                # Use Google Calendar if requested, else local
                if "google" in question.lower():
                    meeting = await self.calendar_service.schedule_google_meeting(user_id or session_id)
                else:
                    meeting = await self.calendar_service.schedule_meeting(user_id or session_id)
                answer = f"A meeting has been scheduled for you. Details: {meeting}"
                self.session_history[session_id].append({"role": "assistant", "content": answer, "calendar": meeting})
                return {
                    "answer": answer,
                    "calendar": meeting,
                    "analysis": analysis,
                    "guardrails": {"status": "safe"}
                }

            # Step 3: Embed question
            embedding = await self.openai_service.generate_embeddings(question)
            # Step 4: Search Pinecone
            kb_results = await self.pinecone_service.search_similar(embedding, top_k=5)
            
            if not kb_results:
                logger.warning("No results found in Pinecone, using fallback response")
                answer = "I'm sorry, I don't have specific information about that in my knowledge base. Please try asking about Aven's services, credit cards, or general information, or contact Aven's customer support directly."
                self.session_history[session_id].append({"role": "assistant", "content": answer})
                return {
                    "answer": answer,
                    "sources": [],
                    "context": "",
                    "guardrails": {"status": "safe"},
                    "analysis": analysis
                }
            
            context = "\n\n".join([r["text"] for r in kb_results if r.get("text")])
            sources = [{"url": r["url"], "score": r["score"]} for r in kb_results]
            # Step 5: Generate answer with OpenAI
            answer = await self.openai_service.generate_response(question, context)
            # Step 6: Guardrails check
            guardrails_result = self.guardrails_service.check_text(answer)
            if guardrails_result["status"] != "safe":
                logger.warning(f"Guardrails triggered: {guardrails_result}")
                fallback = "Sorry, I can't answer that question."
                self.session_history[session_id].append({"role": "assistant", "content": fallback, "guardrails": guardrails_result})
                return {
                    "answer": fallback,
                    "sources": sources,
                    "context": context,
                    "guardrails": guardrails_result,
                    "analysis": analysis
                }
            # If safe, return answer
            self.session_history[session_id].append({"role": "assistant", "content": answer})
            return {
                "answer": answer,
                "sources": sources,
                "context": context,
                "guardrails": guardrails_result,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"AssistantService text Q&A error: {e}")
            return {"error": str(e)}

    async def answer_voice_question(self, audio_stream: AsyncGenerator[bytes, None], session_id: str, user_id: Optional[str] = None, language: str = "en", model: str = "whisper-1", voice: str = "alloy") -> Dict[str, Any]:
        """Transcribe audio, answer question, synthesize spoken answer. Guardrails and calendar integration enforced."""
        try:
            # Step 1: Transcribe audio
            transcription_chunks = []
            async for chunk in self.voice_service.transcribe_audio_stream(audio_stream, language=language, model=model):
                transcription_chunks.append(chunk)
                if chunk.get("type") == "final":
                    break
            transcript = " ".join([c["text"] for c in transcription_chunks if c.get("text")])
            if not transcript.strip():
                return {"error": "No speech detected in audio", "transcription": ""}
            # Step 2: Analyze query
            analysis = self.query_analyzer.analyze_query(transcript)
            logger.info(f"Voice query analysis: {analysis}")
            # Step 3: Calendar trigger
            if analysis.get("calendar_trigger"):
                if "google" in transcript.lower():
                    meeting = await self.calendar_service.schedule_google_meeting(user_id or session_id)
                else:
                    meeting = await self.calendar_service.schedule_meeting(user_id or session_id)
                answer = f"A meeting has been scheduled for you. Details: {meeting}"
                audio_chunks = []
                async for audio_chunk in self.voice_service.synthesize_speech_stream(answer, voice=voice):
                    audio_chunks.append(audio_chunk)
                audio_response = b"".join(audio_chunks)
                self.session_history[session_id].append({"role": "assistant", "content": answer, "calendar": meeting})
                return {
                    "transcription": transcript,
                    "answer": answer,
                    "audio_response": audio_response,
                    "calendar": meeting,
                    "analysis": analysis,
                    "guardrails": {"status": "safe"}
                }
            # Step 4: Answer as text (guardrails enforced)
            text_result = await self.answer_text_question(transcript, session_id, user_id)
            answer = text_result.get("answer", "")
            guardrails_result = text_result.get("guardrails", {})
            # Step 5: Synthesize spoken answer (only if safe)
            audio_response = b""
            if guardrails_result.get("status") == "safe":
                audio_chunks = []
                async for audio_chunk in self.voice_service.synthesize_speech_stream(answer, voice=voice):
                    audio_chunks.append(audio_chunk)
                audio_response = b"".join(audio_chunks)
            else:
                fallback = "Sorry, I can't answer that question."
                audio_chunks = []
                async for audio_chunk in self.voice_service.synthesize_speech_stream(fallback, voice=voice):
                    audio_chunks.append(audio_chunk)
                audio_response = b"".join(audio_chunks)
            return {
                "transcription": transcript,
                "answer": answer,
                "audio_response": audio_response,
                "sources": text_result.get("sources", []),
                "context": text_result.get("context", ""),
                "guardrails": guardrails_result,
                "analysis": text_result.get("analysis", {})
            }
        except Exception as e:
            logger.error(f"AssistantService voice Q&A error: {e}")
            return {"error": str(e)}

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self.session_history.get(session_id, []) 