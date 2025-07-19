import re
import logging
from typing import Dict, List, Tuple, Any
from enum import Enum

logger = logging.getLogger(__name__)

class QueryType(str, Enum):
    GENERAL = "general"
    REALTIME = "realtime"
    PRICING = "pricing"
    FEATURES = "features"
    SUPPORT = "support"
    MEETING = "meeting"

class QueryAnalyzer:
    """Analyzes and classifies user queries"""
    
    def __init__(self):
        # Keywords for real-time search
        self.realtime_keywords = [
            "latest", "current", "recent", "new", "updated", "now", "today",
            "this week", "this month", "latest news", "current status",
            "recent changes", "new features", "latest updates"
        ]
        
        # Keywords for pricing queries
        self.pricing_keywords = [
            "price", "cost", "fee", "rate", "apr", "charges", "pricing",
            "how much", "costs", "fees", "rates", "pricing plan"
        ]
        
        # Keywords for feature queries
        self.feature_keywords = [
            "feature", "functionality", "what can", "how does", "capabilities",
            "benefits", "advantages", "what does", "how to use"
        ]
        
        # Keywords for support queries
        self.support_keywords = [
            "help", "support", "issue", "problem", "error", "trouble",
            "how to", "guide", "tutorial", "assistance", "contact"
        ]
        
        # Keywords for meeting scheduling
        self.meeting_keywords = [
            "schedule", "book", "meeting", "appointment", "call", "demo",
            "consultation", "talk", "discuss", "set up"
        ]
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze a query and return classification and metadata"""
        query_lower = query.lower().strip()
        
        # Determine query type
        query_type = self._classify_query(query_lower)
        
        # Extract entities and intent
        entities = self._extract_entities(query_lower)
        intent = self._determine_intent(query_lower)
        
        # Calculate confidence
        confidence = self._calculate_confidence(query_lower, query_type)
        
        return {
            "query_type": query_type,
            "entities": entities,
            "intent": intent,
            "confidence": confidence,
            "requires_realtime": query_type == QueryType.REALTIME,
            "requires_tools": query_type == QueryType.MEETING
        }
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify the query type based on keywords"""
        if any(keyword in query for keyword in self.realtime_keywords):
            return QueryType.REALTIME
        elif any(keyword in query for keyword in self.meeting_keywords):
            return QueryType.MEETING
        elif any(keyword in query for keyword in self.pricing_keywords):
            return QueryType.PRICING
        elif any(keyword in query for keyword in self.feature_keywords):
            return QueryType.FEATURES
        elif any(keyword in query for keyword in self.support_keywords):
            return QueryType.SUPPORT
        else:
            return QueryType.GENERAL
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract entities from the query"""
        entities = []
        
        # Extract company names
        if "aven" in query:
            entities.append("aven")
        
        # Extract product names
        if "card" in query:
            entities.append("credit_card")
        if "home equity" in query or "heloc" in query:
            entities.append("home_equity")
        
        # Extract time references
        time_patterns = [
            r"today", r"tomorrow", r"this week", r"next week",
            r"this month", r"next month", r"\d{1,2}:\d{2}", r"\d{1,2}am", r"\d{1,2}pm"
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, query)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _determine_intent(self, query: str) -> str:
        """Determine the user's intent"""
        if any(word in query for word in ["what", "how", "when", "where", "why"]):
            return "information_seeking"
        elif any(word in query for word in ["help", "support", "issue", "problem"]):
            return "support_request"
        elif any(word in query for word in ["schedule", "book", "meeting"]):
            return "action_request"
        elif any(word in query for word in ["compare", "vs", "difference"]):
            return "comparison"
        else:
            return "general_inquiry"
    
    def _calculate_confidence(self, query: str, query_type: QueryType) -> float:
        """Calculate confidence score for the classification"""
        base_confidence = 0.5
        
        # Boost confidence based on keyword matches
        if query_type == QueryType.REALTIME:
            matches = sum(1 for keyword in self.realtime_keywords if keyword in query)
            base_confidence += min(matches * 0.2, 0.4)
        elif query_type == QueryType.MEETING:
            matches = sum(1 for keyword in self.meeting_keywords if keyword in query)
            base_confidence += min(matches * 0.2, 0.4)
        elif query_type == QueryType.PRICING:
            matches = sum(1 for keyword in self.pricing_keywords if keyword in query)
            base_confidence += min(matches * 0.2, 0.4)
        
        # Boost confidence for specific entities
        if "aven" in query:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def should_use_realtime_search(self, query: str) -> bool:
        """Determine if real-time search should be used"""
        analysis = self.analyze_query(query)
        return analysis["requires_realtime"]
    
    def should_use_tools(self, query: str) -> bool:
        """Determine if tool calling should be used"""
        analysis = self.analyze_query(query)
        return analysis["requires_tools"] 