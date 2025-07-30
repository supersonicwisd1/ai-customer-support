import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.services.openai_service import OpenAIService
from app.services.pinecone_service import PineconeService

logger = logging.getLogger(__name__)

class RealTimeLearningService:
    """Service for real-time learning and knowledge base improvement"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.pinecone_service = PineconeService()
        self.interaction_log = []
        self.knowledge_gaps = []
        self.improvement_suggestions = []
        
    async def log_interaction(self, interaction_data: Dict[str, Any]):
        """Log user interaction for learning purposes"""
        
        interaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": interaction_data.get("query", ""),
            "response": interaction_data.get("response", ""),
            "user_feedback": interaction_data.get("feedback", None),
            "confidence": interaction_data.get("confidence", 0.0),
            "sources_used": interaction_data.get("sources", []),
            "response_type": interaction_data.get("response_type", "general"),
            "session_id": interaction_data.get("session_id", ""),
            "user_satisfaction": interaction_data.get("satisfaction", None)
        }
        
        self.interaction_log.append(interaction)
        
        # Analyze interaction for learning opportunities
        await self._analyze_interaction_for_learning(interaction)
        
        # Keep only recent interactions (last 1000)
        if len(self.interaction_log) > 1000:
            self.interaction_log = self.interaction_log[-1000:]
    
    async def _analyze_interaction_for_learning(self, interaction: Dict[str, Any]):
        """Analyze interaction to identify learning opportunities"""
        
        query = interaction.get("query", "")
        response = interaction.get("response", "")
        confidence = interaction.get("confidence", 0.0)
        feedback = interaction.get("user_feedback")
        
        # Check for low confidence responses
        if confidence < 0.4:
            await self._identify_knowledge_gap(query, response, confidence)
        
        # Check for negative feedback
        if feedback and feedback.get("rating") in [1, 2]:  # Low ratings
            await self._analyze_negative_feedback(interaction)
        
        # Check for common query patterns
        await self._identify_common_patterns(query, interaction)
        
        # Check for missing information
        await self._identify_missing_information(query, response)
    
    async def _identify_knowledge_gap(self, query: str, response: str, confidence: float):
        """Identify potential knowledge gaps"""
        
        gap_analysis = {
            "query": query,
            "response": response,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "low_confidence",
            "suggested_improvements": []
        }
        
        # Analyze query for missing knowledge areas
        missing_areas = await self._analyze_missing_knowledge_areas(query)
        gap_analysis["missing_areas"] = missing_areas
        
        # Generate improvement suggestions
        suggestions = await self._generate_knowledge_improvement_suggestions(query, missing_areas)
        gap_analysis["suggested_improvements"] = suggestions
        
        self.knowledge_gaps.append(gap_analysis)
        
        logger.info(f"Knowledge gap identified: {query[:50]}... (confidence: {confidence})")
    
    async def _analyze_missing_knowledge_areas(self, query: str) -> List[str]:
        """Analyze query to identify missing knowledge areas"""
        
        analysis_prompt = f"""
        Analyze this customer query to identify what knowledge areas might be missing:
        Query: "{query}"
        
        Identify missing knowledge areas from these categories:
        - Product features and specifications
        - Pricing and fees
        - Application process and requirements
        - Legal and compliance information
        - Technical support and troubleshooting
        - Company information and policies
        - Customer service procedures
        
        Return as a JSON list of missing areas.
        """
        
        try:
            analysis_response = await self.openai_service.generate_response(analysis_prompt, "")
            import json
            missing_areas = json.loads(analysis_response)
            return missing_areas if isinstance(missing_areas, list) else []
        except Exception as e:
            logger.warning(f"Missing knowledge analysis failed: {e}")
            return ["general_information"]
    
    async def _generate_knowledge_improvement_suggestions(self, query: str, missing_areas: List[str]) -> List[str]:
        """Generate suggestions for improving knowledge base"""
        
        suggestions = []
        
        for area in missing_areas:
            if area == "product_features":
                suggestions.append("Add detailed product feature documentation")
            elif area == "pricing_fees":
                suggestions.append("Include comprehensive pricing and fee information")
            elif area == "application_process":
                suggestions.append("Create step-by-step application guides")
            elif area == "legal_compliance":
                suggestions.append("Add legal and compliance documentation")
            elif area == "technical_support":
                suggestions.append("Expand troubleshooting and support documentation")
            elif area == "company_information":
                suggestions.append("Add comprehensive company and policy information")
        
        return suggestions
    
    async def _analyze_negative_feedback(self, interaction: Dict[str, Any]):
        """Analyze negative feedback for improvement opportunities"""
        
        feedback_analysis = {
            "query": interaction.get("query", ""),
            "response": interaction.get("response", ""),
            "feedback": interaction.get("user_feedback", {}),
            "timestamp": datetime.utcnow().isoformat(),
            "type": "negative_feedback",
            "improvement_areas": []
        }
        
        # Analyze what went wrong
        issues = await self._identify_response_issues(interaction)
        feedback_analysis["improvement_areas"] = issues
        
        self.improvement_suggestions.append(feedback_analysis)
        
        logger.info(f"Negative feedback analyzed for query: {interaction.get('query', '')[:50]}...")
    
    async def _identify_response_issues(self, interaction: Dict[str, Any]) -> List[str]:
        """Identify issues with the response"""
        
        query = interaction.get("query", "")
        response = interaction.get("response", "")
        feedback = interaction.get("user_feedback", {})
        
        issues = []
        
        # Check for common issues
        if "not helpful" in feedback.get("comment", "").lower():
            issues.append("response_not_helpful")
        
        if "unclear" in feedback.get("comment", "").lower():
            issues.append("response_unclear")
        
        if "incomplete" in feedback.get("comment", "").lower():
            issues.append("response_incomplete")
        
        if "wrong" in feedback.get("comment", "").lower():
            issues.append("response_incorrect")
        
        # Analyze response quality
        if len(response.split()) < 20:
            issues.append("response_too_short")
        
        if "sorry" in response.lower() and "don't have" in response.lower():
            issues.append("missing_information")
        
        return issues
    
    async def _identify_common_patterns(self, query: str, interaction: Dict[str, Any]):
        """Identify common query patterns for optimization"""
        
        # This could be expanded to track query patterns and optimize responses
        # For now, just log the pattern
        pattern = self._extract_query_pattern(query)
        
        if pattern:
            logger.info(f"Common query pattern identified: {pattern}")
    
    def _extract_query_pattern(self, query: str) -> Optional[str]:
        """Extract common patterns from queries"""
        
        query_lower = query.lower()
        
        patterns = [
            ("pricing", "pricing_inquiry"),
            ("apply", "application_inquiry"),
            ("problem", "troubleshooting"),
            ("contact", "support_request"),
            ("feature", "product_inquiry"),
            ("fee", "pricing_inquiry"),
            ("rate", "pricing_inquiry"),
            ("limit", "product_inquiry"),
            ("approval", "application_inquiry"),
            ("eligibility", "application_inquiry")
        ]
        
        for keyword, pattern in patterns:
            if keyword in query_lower:
                return pattern
        
        return None
    
    async def _identify_missing_information(self, query: str, response: str):
        """Identify when information is missing from responses"""
        
        if "don't have" in response.lower() or "not available" in response.lower():
            missing_info = {
                "query": query,
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "missing_information",
                "suggested_content": await self._suggest_missing_content(query)
            }
            
            self.knowledge_gaps.append(missing_info)
            logger.info(f"Missing information identified for query: {query[:50]}...")
    
    async def _suggest_missing_content(self, query: str) -> str:
        """Suggest content that should be added to knowledge base"""
        
        suggestion_prompt = f"""
        This query needs information that's not currently in our knowledge base:
        Query: "{query}"
        
        Suggest what content should be added to help answer this type of query.
        Focus on specific, actionable content that would be helpful.
        """
        
        try:
            suggestion = await self.openai_service.generate_response(suggestion_prompt, "")
            return suggestion
        except Exception as e:
            logger.warning(f"Content suggestion failed: {e}")
            return "Additional information needed for this query type"
    
    async def generate_learning_report(self) -> Dict[str, Any]:
        """Generate a learning report based on recent interactions"""
        
        recent_interactions = self.interaction_log[-100:]  # Last 100 interactions
        
        if not recent_interactions:
            return {"message": "No recent interactions to analyze"}
        
        # Analyze interaction patterns
        total_interactions = len(recent_interactions)
        low_confidence_count = len([i for i in recent_interactions if i.get("confidence", 0) < 0.4])
        negative_feedback_count = len([i for i in recent_interactions if i.get("user_feedback", {}).get("rating") in [1, 2]])
        
        # Identify common query types
        query_types: Dict[str, int] = defaultdict(int)
        for interaction in recent_interactions:
            pattern = self._extract_query_pattern(interaction.get("query", ""))
            if pattern:
                query_types[pattern] += 1
        
        # Generate improvement recommendations
        recommendations = await self._generate_improvement_recommendations(recent_interactions)
        
        return {
            "report_period": {
                "start": recent_interactions[0]["timestamp"],
                "end": recent_interactions[-1]["timestamp"]
            },
            "interaction_summary": {
                "total_interactions": total_interactions,
                "low_confidence_rate": round(low_confidence_count / total_interactions * 100, 2),
                "negative_feedback_rate": round(negative_feedback_count / total_interactions * 100, 2),
                "average_confidence": round(sum(i.get("confidence", 0) for i in recent_interactions) / total_interactions, 2)
            },
            "query_patterns": dict(query_types),
            "knowledge_gaps": len(self.knowledge_gaps),
            "improvement_suggestions": len(self.improvement_suggestions),
            "recommendations": recommendations
        }
    
    async def _generate_improvement_recommendations(self, interactions: List[Dict[str, Any]]) -> List[str]:
        """Generate specific improvement recommendations"""
        
        recommendations = []
        
        # Analyze patterns
        low_confidence_queries = [i for i in interactions if i.get("confidence", 0) < 0.4]
        negative_feedback_queries = [i for i in interactions if i.get("user_feedback", {}).get("rating") in [1, 2]]
        
        if low_confidence_queries:
            recommendations.append("Expand knowledge base for low-confidence query types")
        
        if negative_feedback_queries:
            recommendations.append("Improve response quality for queries with negative feedback")
        
        # Check for missing information patterns
        missing_info_count = len([i for i in interactions if "don't have" in i.get("response", "").lower()])
        if missing_info_count > 5:
            recommendations.append("Add missing information to knowledge base")
        
        # Check for common query types that need better coverage
        query_types: Dict[str, int] = defaultdict(int)
        for interaction in interactions:
            pattern = self._extract_query_pattern(interaction.get("query", ""))
            if pattern:
                query_types[pattern] += 1
        
        for query_type, count in query_types.items():
            if count > 10:  # If a query type appears frequently
                recommendations.append(f"Improve coverage for {query_type} queries")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def update_knowledge_base_from_learning(self):
        """Update knowledge base based on learning insights"""
        
        # This would integrate with the enhanced knowledge service
        # to actually add new content to the knowledge base
        
        if self.knowledge_gaps:
            logger.info(f"Processing {len(self.knowledge_gaps)} knowledge gaps for knowledge base update")
            
            # Process knowledge gaps and add to knowledge base
            for gap in self.knowledge_gaps[-10:]:  # Process last 10 gaps
                await self._add_knowledge_from_gap(gap)
        
        # Clear processed gaps
        self.knowledge_gaps = []
    
    async def _add_knowledge_from_gap(self, gap: Dict[str, Any]):
        """Add knowledge to the database based on identified gap"""
        
        query = gap.get("query", "")
        suggested_improvements = gap.get("suggested_improvements", [])
        
        if suggested_improvements:
            # Generate content based on suggestions
            content = await self._generate_content_for_gap(query, suggested_improvements)
            
            if content:
                # Add to knowledge base
                await self._add_to_knowledge_base(content)
                logger.info(f"Added knowledge for gap: {query[:50]}...")
    
    async def _generate_content_for_gap(self, query: str, improvements: List[str]) -> Optional[Dict[str, Any]]:
        """Generate content to fill a knowledge gap"""
        
        content_prompt = f"""
        Generate helpful content to address this knowledge gap:
        Query: "{query}"
        Needed improvements: {', '.join(improvements)}
        
        Create comprehensive, accurate content that would help answer this type of query.
        Include relevant details about Aven's products and services.
        """
        
        try:
            content = await self.openai_service.generate_response(content_prompt, "")
            
            return {
                "content": content,
                "source": "ai_generated",
                "query_type": self._extract_query_pattern(query),
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "generated_for_gap": True,
                    "original_query": query
                }
            }
        except Exception as e:
            logger.warning(f"Content generation for gap failed: {e}")
            return None
    
    async def _add_to_knowledge_base(self, content: Dict[str, Any]):
        """Add content to the knowledge base"""
        
        try:
            # Generate embedding
            embedding = await self.openai_service.generate_embeddings(content["content"])
            
            # Prepare document for storage
            document = {
                "id": f"learned_{hash(content['content'][:100])}",
                "text": content["content"],
                "embedding": embedding,
                "source": content["source"],
                "timestamp": content["timestamp"],
                "metadata": content.get("metadata", {})
            }
            
            # Store in Pinecone
            await self.pinecone_service.upsert_documents([document])
            
        except Exception as e:
            logger.error(f"Failed to add content to knowledge base: {e}")
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get current learning insights"""
        
        return {
            "total_interactions": len(self.interaction_log),
            "knowledge_gaps": len(self.knowledge_gaps),
            "improvement_suggestions": len(self.improvement_suggestions),
            "recent_activity": {
                "last_interaction": self.interaction_log[-1]["timestamp"] if self.interaction_log else None,
                "interactions_today": len([i for i in self.interaction_log if i["timestamp"].startswith(datetime.utcnow().strftime("%Y-%m-%d"))])
            }
        } 