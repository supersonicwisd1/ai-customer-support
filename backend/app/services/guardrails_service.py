import logging
import os
import re
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)

class GuardrailsService:
    """Checks text for safety, compliance, and brand alignment using OpenAI Moderation API and custom rules."""
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)
        
        # Financial compliance keywords
        self.financial_forbidden = [
            "financial advice", "investment advice", "loan guarantee", "credit guarantee",
            "investment recommendation", "stock recommendation", "buy this stock",
            "sell this stock", "financial planning", "retirement planning",
            "tax advice", "legal advice", "medical advice", "health advice"
        ]
        
        # Personal information protection
        self.personal_info_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone number
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP address
        ]
        
        # Brand safety keywords
        self.brand_safety_keywords = [
            "competitor", "better than", "worse than", "switch to", "leave aven",
            "cancel account", "close account", "delete account", "hate aven",
            "aven sucks", "aven is bad", "aven sucks", "aven terrible"
        ]
        
        # Profanity and inappropriate content
        self.inappropriate_keywords = [
            "profanity1", "profanity2", "hate speech", "discrimination",
            "harassment", "bullying", "threat", "violence"
        ]

    def check_text(self, text: str) -> Dict[str, Any]:
        """Check text for safety and compliance. Returns dict with status, reason, categories."""
        try:
            # 1. Check for personal information
            personal_info_check = self._check_personal_info(text)
            if personal_info_check["status"] != "safe":
                return personal_info_check
            
            # 2. Check financial compliance
            financial_check = self._check_financial_compliance(text)
            if financial_check["status"] != "safe":
                return financial_check
            
            # 3. Check brand safety
            brand_check = self._check_brand_safety(text)
            if brand_check["status"] != "safe":
                return brand_check
            
            # 4. Check inappropriate content
            inappropriate_check = self._check_inappropriate_content(text)
            if inappropriate_check["status"] != "safe":
                return inappropriate_check
            
            # 5. Check with OpenAI Moderation API
            openai_check = self._check_openai_moderation(text)
            if openai_check["status"] != "safe":
                return openai_check
            
            # 6. If passed all checks
            return {"status": "safe", "reason": "", "categories": []}
            
        except Exception as e:
            logger.error(f"GuardrailsService error: {e}")
            return {"status": "error", "reason": str(e), "categories": []}
    
    def _check_personal_info(self, text: str) -> Dict[str, Any]:
        """Check for personal information patterns"""
        for pattern in self.personal_info_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Blocked for personal information pattern: {pattern}")
                return {
                    "status": "blocked",
                    "reason": "Contains personal information",
                    "categories": ["personal_info"]
                }
        return {"status": "safe", "reason": "", "categories": []}
    
    def _check_financial_compliance(self, text: str) -> Dict[str, Any]:
        """Check for financial compliance violations"""
        text_lower = text.lower()
        for keyword in self.financial_forbidden:
            if keyword.lower() in text_lower:
                logger.warning(f"Blocked for financial compliance: {keyword}")
                return {
                    "status": "blocked",
                    "reason": f"Contains financial advice: {keyword}",
                    "categories": ["financial_advice"]
                }
        return {"status": "safe", "reason": "", "categories": []}
    
    def _check_brand_safety(self, text: str) -> Dict[str, Any]:
        """Check for brand safety issues"""
        text_lower = text.lower()
        for keyword in self.brand_safety_keywords:
            if keyword.lower() in text_lower:
                logger.warning(f"Blocked for brand safety: {keyword}")
                return {
                    "status": "blocked",
                    "reason": f"Contains brand safety concern: {keyword}",
                    "categories": ["brand_safety"]
                }
        return {"status": "safe", "reason": "", "categories": []}
    
    def _check_inappropriate_content(self, text: str) -> Dict[str, Any]:
        """Check for inappropriate content"""
        text_lower = text.lower()
        for keyword in self.inappropriate_keywords:
            if keyword.lower() in text_lower:
                logger.warning(f"Blocked for inappropriate content: {keyword}")
                return {
                    "status": "blocked",
                    "reason": f"Contains inappropriate content: {keyword}",
                    "categories": ["inappropriate"]
                }
        return {"status": "safe", "reason": "", "categories": []}
    
    def _check_openai_moderation(self, text: str) -> Dict[str, Any]:
        """Check with OpenAI Moderation API"""
        try:
            response = self.client.moderations.create(input=text)
            result = response.results[0]
            if result.flagged:
                logger.warning(f"Flagged by OpenAI Moderation: {result.categories}")
                return {
                    "status": "flagged",
                    "reason": "Flagged by OpenAI Moderation API",
                    "categories": [k for k, v in result.categories.items() if v]
                }
            return {"status": "safe", "reason": "", "categories": []}
        except Exception as e:
            logger.error(f"OpenAI Moderation API error: {e}")
            return {"status": "error", "reason": f"Moderation API error: {str(e)}", "categories": []} 