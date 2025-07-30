import logging
import os
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
        # Example: Add your own forbidden keywords or phrases
        self.forbidden_keywords = [
            "financial advice", "investment advice", "loan guarantee", "medical advice", "personal information",
            "social security number", "credit card number", "password", "profanity1", "profanity2"
        ]

    def check_text(self, text: str) -> Dict[str, Any]:
        """Check text for safety and compliance. Returns dict with status, reason, categories."""
        try:
            # 1. Check forbidden keywords (simple rule-based)
            for keyword in self.forbidden_keywords:
                if keyword.lower() in text.lower():
                    logger.warning(f"Blocked for forbidden keyword: {keyword}")
                    return {
                        "status": "blocked",
                        "reason": f"Contains forbidden keyword: {keyword}",
                        "categories": ["forbidden_keyword"]
                    }
            # 2. Check with OpenAI Moderation API
            response = self.client.moderations.create(input=text)
            result = response.results[0]
            if result.flagged:
                logger.warning(f"Flagged by OpenAI Moderation: {result.categories}")
                return {
                    "status": "flagged",
                    "reason": "Flagged by OpenAI Moderation API",
                    "categories": [k for k, v in result.categories.items() if v]
                }
            # 3. If passed all checks
            return {"status": "safe", "reason": "", "categories": []}
        except Exception as e:
            logger.error(f"GuardrailsService error: {e}")
            return {"status": "error", "reason": str(e), "categories": []} 