import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService

logger = logging.getLogger(__name__)

class IntelligentResponseService:
    """Enhanced response service with better context understanding and response generation"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.pinecone_service = PineconeService()
        
    async def generate_intelligent_response(self, query: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate intelligent response with enhanced context understanding"""
        
        try:
            logger.info(f"Processing intelligent response for query: {query[:100]}...")
            
            # Step 1: Enhanced query analysis
            query_analysis = await self._analyze_query_intelligently(query)
            logger.debug(f"Query analysis completed: {query_analysis.get('intent', 'unknown')}")
            
            # Step 2: Multi-source knowledge retrieval
            knowledge_results = await self._retrieve_multi_source_knowledge(query, query_analysis)
            logger.debug(f"Knowledge retrieval completed: {len(knowledge_results.get('results', []))} results")
            
            # Step 3: Context-aware response generation
            response = await self._generate_context_aware_response(query, knowledge_results, user_context)
            logger.debug(f"Response generation completed: {len(response.get('answer', '')[:100])} chars")
            
            # Step 4: Response enhancement and validation
            enhanced_response = await self._enhance_response_quality(response, query_analysis)
            logger.info(f"Intelligent response completed successfully")
            
            return {
                "answer": enhanced_response["answer"],
                "sources": enhanced_response["sources"],
                "confidence": enhanced_response["confidence"],
                "context_used": enhanced_response["context_used"],
                "query_analysis": query_analysis,
                "response_type": enhanced_response["response_type"],
                "suggestions": enhanced_response["suggestions"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Intelligent response generation error: {e}")
            return {
                "answer": "I apologize, but I'm having trouble processing your request right now. Please try again or contact Aven's customer support for immediate assistance.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _analyze_query_intelligently(self, query: str) -> Dict[str, Any]:
        """Enhanced query analysis with intent classification and entity extraction"""
        
        analysis_prompt = f"""
        Analyze this customer query about Aven (a financial technology company):
        Query: "{query}"
        
        Provide a detailed analysis in valid JSON format with the following structure:
        {{
            "intent": "information_seeking|problem_solving|application_help|pricing_inquiry|general_inquiry",
            "entities": ["product1", "product2"],
            "urgency": "low|medium|high",
            "complexity": "simple|moderate|complex",
            "domains": ["product", "legal", "support", "technical", "general"],
            "tone": "professional|friendly|technical|casual",
            "follow_up_suggestions": ["suggestion1", "suggestion2"]
        }}
        
        Important: Return ONLY valid JSON, no additional text.
        """
        
        try:
            analysis_response = await self.openai_service.generate_response(analysis_prompt, "")
            
            # Clean the response to ensure it's valid JSON
            analysis_response = analysis_response.strip()
            
            # Remove any markdown formatting if present
            if analysis_response.startswith("```json"):
                analysis_response = analysis_response.replace("```json", "").replace("```", "").strip()
            elif analysis_response.startswith("```"):
                analysis_response = analysis_response.replace("```", "").strip()
            
            # Parse the JSON response
            import json
            analysis = json.loads(analysis_response)
            
            # Validate required fields
            required_fields = ["intent", "entities", "urgency", "complexity", "domains", "tone"]
            for field in required_fields:
                if field not in analysis:
                    analysis[field] = "general" if field == "domains" else "medium" if field in ["urgency", "complexity"] else "information_seeking" if field == "intent" else "professional" if field == "tone" else []
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Query analysis failed, using fallback: {e}")
            return {
                "intent": "information_seeking",
                "entities": [],
                "urgency": "medium",
                "complexity": "moderate",
                "domains": ["general"],
                "tone": "professional",
                "follow_up_suggestions": []
            }
    
    async def _retrieve_multi_source_knowledge(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve knowledge from multiple sources based on query analysis"""
        
        # Generate embedding for the query
        query_embedding = await self.openai_service.generate_embeddings(query)
        
        # Search Pinecone with different strategies based on analysis
        search_results = []
        
        # Primary search
        primary_results = await self.pinecone_service.search_similar(query_embedding, top_k=5)
        search_results.extend(primary_results)
        
        # Domain-specific searches if needed
        domains = analysis.get("domains", [])
        for domain in domains:
            if domain in ["product", "legal", "support", "technical"]:
                # Add domain-specific context to query
                domain_query = f"{query} {domain} information"
                domain_embedding = await self.openai_service.generate_embeddings(domain_query)
                domain_results = await self.pinecone_service.search_similar(domain_embedding, top_k=3)
                search_results.extend(domain_results)
        
        # Remove duplicates and sort by relevance
        unique_results = self._deduplicate_results(search_results)
        
        return {
            "primary_results": primary_results,
            "domain_results": unique_results,
            "total_results": len(unique_results),
            "domains_searched": domains
        }
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity"""
        unique_results = []
        seen_content = set()
        
        for result in results:
            content_hash = hash(result.get("text", "")[:100])  # Hash first 100 chars
            if content_hash not in seen_content:
                unique_results.append(result)
                seen_content.add(content_hash)
        
        # Sort by score
        unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return unique_results
    
    async def _generate_context_aware_response(self, query: str, knowledge_results: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate context-aware response using retrieved knowledge"""
        
        # Prepare context from knowledge results
        context_parts = []
        sources = []
        
        for result in knowledge_results.get("primary_results", []):
            if result.get("text"):
                context_parts.append(result["text"])
                sources.append({
                    "url": result.get("url", ""),
                    "score": result.get("score", 0),
                    "type": "primary"
                })
        
        context = "\n\n".join(context_parts)
        
        # Create enhanced prompt based on query analysis
        response_prompt = self._create_enhanced_prompt(query, context, user_context)
        
        # Generate response
        answer = await self.openai_service.generate_response(response_prompt, context)
        
        return {
            "answer": answer,
            "sources": sources,
            "context_used": context,
            "confidence": self._calculate_confidence(knowledge_results),
            "response_type": self._determine_response_type(query, answer)
        }
    
    def _create_enhanced_prompt(self, query: str, context: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Create an enhanced prompt for better response generation"""
        
        base_prompt = f"""
        You are Aven AI's customer care assistant. Aven is a financial technology company that offers:
        - Home equity-backed credit cards
        - Home Equity Lines of Credit (HELOC)
        - Financial services through Coastal Community Bank (FDIC insured)
        
        Customer Query: "{query}"
        
        Available Context Information:
        {context}
        
        Instructions:
        1. Provide accurate, helpful information based on the context
        2. Be professional yet friendly
        3. If information is not available in the context, acknowledge this and suggest contacting support
        4. Include relevant details about Aven's products and services
        5. Mention FDIC insurance and banking partnerships when relevant
        6. Provide actionable next steps when appropriate
        7. Keep responses concise but comprehensive
        
        User Context: {user_context or 'No additional context provided'}
        
        Please provide a helpful response:
        """
        
        return base_prompt
    
    def _calculate_confidence(self, knowledge_results: Dict[str, Any]) -> float:
        """Calculate confidence score based on knowledge retrieval results"""
        
        total_results = knowledge_results.get("total_results", 0)
        primary_results = knowledge_results.get("primary_results", [])
        
        if not primary_results:
            return 0.3  # Low confidence if no results
        
        # Calculate average score of top results
        scores = [r.get("score", 0) for r in primary_results[:3]]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Adjust confidence based on number of results and scores
        confidence = min(0.9, avg_score + (total_results * 0.1))
        
        return round(confidence, 2)
    
    def _determine_response_type(self, query: str, answer: str) -> str:
        """Determine the type of response generated"""
        
        query_lower = query.lower()
        answer_lower = answer.lower()
        
        if any(word in query_lower for word in ["how", "what", "when", "where", "why"]):
            return "informational"
        elif any(word in query_lower for word in ["problem", "issue", "error", "trouble"]):
            return "troubleshooting"
        elif any(word in query_lower for word in ["apply", "application", "sign up", "register"]):
            return "application_guidance"
        elif any(word in query_lower for word in ["price", "cost", "fee", "rate"]):
            return "pricing_information"
        elif any(word in query_lower for word in ["contact", "support", "help"]):
            return "support_direction"
        else:
            return "general_information"
    
    async def _enhance_response_quality(self, response: Dict[str, Any], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance response quality with additional features"""
        
        enhanced_response = response.copy()
        
        # Add response suggestions based on query analysis
        suggestions = await self._generate_follow_up_suggestions(query_analysis, response)
        enhanced_response["suggestions"] = suggestions
        
        # Add confidence indicators
        confidence = enhanced_response.get("confidence", 0.5)
        if confidence < 0.4:
            enhanced_response["answer"] += "\n\nNote: If you need more specific information, please contact Aven's customer support team for personalized assistance."
        
        # Add contact information for complex queries
        if query_analysis.get("complexity") == "complex":
            enhanced_response["answer"] += "\n\nFor detailed assistance with your specific situation, please contact Aven's support team at support@aven.com or visit https://www.aven.com/support."
        
        return enhanced_response
    
    async def _generate_follow_up_suggestions(self, query_analysis: Dict[str, Any], response: Dict[str, Any]) -> List[str]:
        """Generate follow-up question suggestions"""
        
        intent = query_analysis.get("intent", "information_seeking")
        response_type = response.get("response_type", "general_information")
        
        suggestions = []
        
        if intent == "information_seeking":
            suggestions.extend([
                "Would you like to learn more about Aven's credit card features?",
                "Are you interested in applying for an Aven credit card?",
                "Do you have questions about our HELOC products?"
            ])
        
        elif intent == "problem_solving":
            suggestions.extend([
                "Would you like me to help you contact our support team?",
                "Do you need assistance with your account?",
                "Would you like to schedule a call with our customer service?"
            ])
        
        elif intent == "application_help":
            suggestions.extend([
                "Would you like to start the application process?",
                "Do you have questions about eligibility requirements?",
                "Would you like to learn about the approval process?"
            ])
        
        # Add general suggestions
        suggestions.extend([
            "Is there anything else I can help you with today?",
            "Would you like to learn more about Aven's services?"
        ])
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    async def generate_conversational_response(self, query: str, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate response considering conversation history"""
        
        # Include conversation context
        conversation_context = self._build_conversation_context(conversation_history)
        
        # Add conversation context to user context
        user_context = {
            "conversation_history": conversation_context,
            "conversation_length": len(conversation_history)
        }
        
        return await self.generate_intelligent_response(query, user_context)
    
    def _build_conversation_context(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Build context from conversation history"""
        
        if not conversation_history:
            return ""
        
        # Take last 3 exchanges for context
        recent_exchanges = conversation_history[-6:]  # Last 3 Q&A pairs
        
        context_parts = []
        for exchange in recent_exchanges:
            if exchange.get("role") == "user":
                context_parts.append(f"User: {exchange.get('content', '')}")
            elif exchange.get("role") == "assistant":
                context_parts.append(f"Assistant: {exchange.get('content', '')}")
        
        return "\n".join(context_parts) 