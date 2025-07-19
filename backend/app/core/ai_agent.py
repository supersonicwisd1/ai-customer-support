import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.models.chat import ChatRequest, ChatResponse
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService
from app.services.search_service import SearchService
from app.core.vector_store import VectorStore
from app.core.query_analyzer import QueryAnalyzer, QueryType
from app.core.guardrails import GuardrailsService, SafetyLevel

logger = logging.getLogger(__name__)

class AIAgent:
    """Main AI agent that orchestrates chat, search, and safety"""
    
    def __init__(self, openai_service: OpenAIService, pinecone_service: PineconeService):
        self.openai_service = openai_service
        self.pinecone_service = pinecone_service
        self.search_service = SearchService()
        self.vector_store = VectorStore(pinecone_service, openai_service)
        self.query_analyzer = QueryAnalyzer()
        self.guardrails = GuardrailsService()
        
        logger.info("AI Agent initialized successfully with guardrails")
    
    async def process_chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request with comprehensive safety checks"""
        start_time = datetime.utcnow()
        
        try:
            # Generate a simple user ID for safety checks
            user_id = f"user_{hash(request.session_id) % 10000}" if request.session_id else "anonymous"
            
            # Step 1: Safety check on user input
            logger.info(f"Processing chat request: {request.message[:50]}...")
            
            input_safety = self.guardrails.check_user_input(user_id, request.message, request.session_id)
            
            if input_safety.level == SafetyLevel.BLOCKED:
                logger.warning(f"User input blocked: {input_safety.reason}")
                return ChatResponse(
                    message="I'm sorry, but I cannot process that request. Please ensure your message is appropriate and doesn't contain sensitive information.",
                    sources=[],
                    confidence=0.0,
                    session_id=request.session_id,
                    timestamp=datetime.utcnow().isoformat(),
                    processing_time=(datetime.utcnow() - start_time).total_seconds(),
                    tokens_used=None,
                    safety_level=input_safety.level.value,
                    safety_reason=input_safety.reason
                )
            
            if input_safety.level == SafetyLevel.WARNING:
                logger.info(f"User input warning: {input_safety.reason}")
            
            # Step 2: Analyze query type
            query_analysis = self.query_analyzer.analyze_query(request.message)
            logger.info(f"Query analysis: {query_analysis}")
            
            # Step 3: Get relevant context
            context = await self._get_context(request.message, query_analysis)
            
            # Step 4: Generate AI response
            ai_response = await self._generate_response(request.message, context, query_analysis)
            
            # Step 5: Safety check on AI response
            response_safety = self.guardrails.check_ai_response(ai_response, user_id, request.message)
            
            if response_safety.level == SafetyLevel.BLOCKED:
                logger.warning(f"AI response blocked: {response_safety.reason}")
                ai_response = "I apologize, but I cannot provide that information. Please try rephrasing your question."
            
            if response_safety.level == SafetyLevel.WARNING:
                logger.info(f"AI response warning: {response_safety.reason}")
            
            # Step 6: Prepare response
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            response = ChatResponse(
                message=ai_response,
                sources=context.get('sources', []),
                confidence=query_analysis.get('confidence', 0.8),
                session_id=request.session_id,
                timestamp=datetime.utcnow().isoformat(),
                processing_time=processing_time,
                tokens_used=None,
                safety_level=response_safety.level.value,
                safety_reason=response_safety.reason
            )
            
            logger.info("Chat response generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing chat: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ChatResponse(
                message="I apologize, but I encountered an error processing your request. Please try again.",
                sources=[],
                confidence=0.0,
                session_id=request.session_id,
                timestamp=datetime.utcnow().isoformat(),
                processing_time=processing_time,
                tokens_used=None,
                safety_level="error",
                safety_reason=f"Processing error: {str(e)}"
            )
    
    async def _get_context(self, message: str, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant context for the query"""
        context = {
            'knowledge_base': [],
            'search_results': [],
            'sources': []
        }
        
        try:
            # Get knowledge base context
            kb_results = await self.vector_store.search_similar(message, top_k=3)
            if kb_results:
                context['knowledge_base'] = [result.get('text', '') for result in kb_results]
                context['sources'].extend([result.get('url', '') for result in kb_results if result.get('url')])
            
            # Get real-time search if needed
            if query_analysis.get('requires_realtime', False):
                logger.info("Performing real-time search")
                search_results = await self.search_service.search(message, max_results=3)
                if search_results:
                    context['search_results'] = [result.content for result in search_results]
                    context['sources'].extend([result.url for result in search_results if result.url])
            
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
        
        return context
    
    async def _generate_response(self, message: str, context: Dict[str, Any], query_analysis: Dict[str, Any]) -> str:
        """Generate AI response with context"""
        try:
            # Prepare system prompt
            system_prompt = self._build_system_prompt(context, query_analysis)
            
            # Prepare user message
            user_message = f"User question: {message}\n\nPlease provide a helpful, accurate response based on the available information."
            
            # Generate response
            response = await self.openai_service.generate_response(user_message, system_prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error generating a response. Please try again."
    
    def _build_system_prompt(self, context: Dict[str, Any], query_analysis: Dict[str, Any]) -> str:
        """Build system prompt with context and safety guidelines"""
        
        # Base prompt
        prompt = """You are Aven AI Assistant, a helpful customer support agent for Aven (aven.com). 

Your role is to provide accurate, helpful information about Aven's services, products, and policies. Always be professional, friendly, and transparent about the sources of your information.

SAFETY GUIDELINES:
- Never share personal, financial, or sensitive information
- If asked about private data, politely decline and suggest contacting support
- If you're unsure about information, say so rather than guessing
- Always prioritize user safety and data protection
- If a request seems inappropriate, politely redirect to appropriate channels

RESPONSE GUIDELINES:
- Be concise but comprehensive
- Cite sources when available
- If information is from real-time search, mention it's current
- If information is from knowledge base, mention it's from our documentation
- Always maintain Aven's professional tone and brand voice"""

        # Add context
        if context.get('knowledge_base'):
            prompt += "\n\nKNOWLEDGE BASE CONTEXT:\n"
            for i, content in enumerate(context['knowledge_base'], 1):
                prompt += f"{i}. {content[:300]}...\n"
        
        if context.get('search_results'):
            prompt += "\n\nREAL-TIME SEARCH CONTEXT:\n"
            for i, content in enumerate(context['search_results'], 1):
                prompt += f"{i}. {content[:300]}...\n"
        
        # Add query type context
        query_type = query_analysis.get('query_type', QueryType.GENERAL)
        if query_type == QueryType.REALTIME:
            prompt += "\n\nNOTE: This query requires current information. Use real-time search results when available."
        elif query_type == QueryType.FEATURES:
            prompt += "\n\nNOTE: This query is best answered from our knowledge base and documentation."
        
        return prompt
    
    async def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety statistics"""
        return self.guardrails.get_safety_stats()
    
    async def export_safety_log(self) -> str:
        """Export safety log"""
        return self.guardrails.export_safety_log()
