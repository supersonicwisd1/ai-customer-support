import logging
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class SafetyLevel(Enum):
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"
    CRITICAL = "critical"

@dataclass
class SafetyCheck:
    level: SafetyLevel
    reason: str
    details: Dict[str, Any]
    timestamp: datetime

class GuardrailsService:
    """Comprehensive safety and content filtering service"""
    
    def __init__(self):
        # Content filtering patterns
        self.inappropriate_patterns = [
            r'\b(hate|racist|sexist|discriminatory)\b',
            r'\b(violence|kill|murder|attack)\b',
            r'\b(drugs|illegal|unlawful)\b',
            r'\b(personal|private|confidential)\s+(info|information|data)',
            r'\b(ssn|social\s+security|credit\s+card\s+number|bank\s+account)',
            r'\b(password|pin|security\s+code)',
            r'\b(admin|root|sudo|privileged)',
            r'\b(exploit|hack|breach|vulnerability)',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.inappropriate_patterns]
        
        # Rate limiting
        self.rate_limits = {
            'requests_per_minute': 30,
            'requests_per_hour': 300,
            'requests_per_day': 1000,
        }
        
        # User request tracking
        self.user_requests = defaultdict(list)
        self.blocked_users = set()
        
        # Response monitoring
        self.response_log = []
        self.flagged_responses = []
        
        # Safety thresholds
        self.safety_thresholds = {
            'max_response_length': 5000,
            'max_input_length': 2000,
            'suspicious_keywords_threshold': 3,
            'rate_limit_violations_threshold': 5,
        }
        
        logger.info("Guardrails service initialized successfully")
    
    def check_user_input(self, user_id: str, message: str, session_id: Optional[str] = None) -> SafetyCheck:
        """Comprehensive check of user input for safety and appropriateness"""
        try:
            # Basic validation
            if not message or not message.strip():
                return SafetyCheck(
                    level=SafetyLevel.BLOCKED,
                    reason="Empty or invalid message",
                    details={"message_length": len(message) if message else 0},
                    timestamp=datetime.utcnow()
                )
            
            # Length check
            if len(message) > self.safety_thresholds['max_input_length']:
                return SafetyCheck(
                    level=SafetyLevel.WARNING,
                    reason="Message too long",
                    details={"message_length": len(message), "max_allowed": self.safety_thresholds['max_input_length']},
                    timestamp=datetime.utcnow()
                )
            
            # Rate limiting check
            rate_check = self._check_rate_limit(user_id)
            if rate_check.level == SafetyLevel.BLOCKED:
                return rate_check
            
            # Content filtering
            content_check = self._check_content_safety(message)
            if content_check.level in [SafetyLevel.BLOCKED, SafetyLevel.CRITICAL]:
                return content_check
            
            # PII detection
            pii_check = self._check_pii(message)
            if pii_check.level == SafetyLevel.BLOCKED:
                return pii_check
            
            # Suspicious activity detection
            suspicious_check = self._check_suspicious_activity(user_id, message)
            if suspicious_check.level == SafetyLevel.BLOCKED:
                return suspicious_check
            
            # All checks passed
            return SafetyCheck(
                level=SafetyLevel.SAFE,
                reason="Input passed all safety checks",
                details={"checks_passed": ["length", "rate_limit", "content", "pii", "suspicious"]},
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error in user input check: {str(e)}")
            return SafetyCheck(
                level=SafetyLevel.BLOCKED,
                reason="Safety check error",
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )
    
    def check_ai_response(self, response: str, user_id: str, original_query: str) -> SafetyCheck:
        """Check AI response for safety and appropriateness"""
        try:
            # Length check
            if len(response) > self.safety_thresholds['max_response_length']:
                return SafetyCheck(
                    level=SafetyLevel.WARNING,
                    reason="Response too long",
                    details={"response_length": len(response), "max_allowed": self.safety_thresholds['max_response_length']},
                    timestamp=datetime.utcnow()
                )
            
            # Content filtering
            content_check = self._check_content_safety(response)
            if content_check.level in [SafetyLevel.BLOCKED, SafetyLevel.CRITICAL]:
                return content_check
            
            # Hallucination detection (basic)
            hallucination_check = self._check_hallucination(response, original_query)
            if hallucination_check.level == SafetyLevel.WARNING:
                return hallucination_check
            
            # Log response for monitoring
            self._log_response(response, user_id, original_query)
            
            return SafetyCheck(
                level=SafetyLevel.SAFE,
                reason="Response passed safety checks",
                details={"checks_passed": ["length", "content", "hallucination"]},
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error in AI response check: {str(e)}")
            return SafetyCheck(
                level=SafetyLevel.WARNING,
                reason="Response safety check error",
                details={"error": str(e)},
                timestamp=datetime.utcnow()
            )
    
    def _check_rate_limit(self, user_id: str) -> SafetyCheck:
        """Check if user has exceeded rate limits"""
        now = datetime.utcnow()
        user_requests = self.user_requests[user_id]
        
        # Clean old requests
        user_requests[:] = [req for req in user_requests if now - req < timedelta(days=1)]
        
        # Check limits
        requests_last_minute = len([req for req in user_requests if now - req < timedelta(minutes=1)])
        requests_last_hour = len([req for req in user_requests if now - req < timedelta(hours=1)])
        requests_last_day = len(user_requests)
        
        if requests_last_minute > self.rate_limits['requests_per_minute']:
            return SafetyCheck(
                level=SafetyLevel.BLOCKED,
                reason="Rate limit exceeded (per minute)",
                details={"requests_last_minute": requests_last_minute, "limit": self.rate_limits['requests_per_minute']},
                timestamp=now
            )
        
        if requests_last_hour > self.rate_limits['requests_per_hour']:
            return SafetyCheck(
                level=SafetyLevel.BLOCKED,
                reason="Rate limit exceeded (per hour)",
                details={"requests_last_hour": requests_last_hour, "limit": self.rate_limits['requests_per_hour']},
                timestamp=now
            )
        
        if requests_last_day > self.rate_limits['requests_per_day']:
            return SafetyCheck(
                level=SafetyLevel.BLOCKED,
                reason="Rate limit exceeded (per day)",
                details={"requests_last_day": requests_last_day, "limit": self.rate_limits['requests_per_day']},
                timestamp=now
            )
        
        # Add current request
        user_requests.append(now)
        
        return SafetyCheck(
            level=SafetyLevel.SAFE,
            reason="Rate limit check passed",
            details={"requests_last_minute": requests_last_minute, "requests_last_hour": requests_last_hour},
            timestamp=now
        )
    
    def _check_content_safety(self, text: str) -> SafetyCheck:
        """Check text for inappropriate content"""
        text_lower = text.lower()
        matched_patterns = []
        
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                matched_patterns.append(pattern.pattern)
        
        if len(matched_patterns) >= self.safety_thresholds['suspicious_keywords_threshold']:
            return SafetyCheck(
                level=SafetyLevel.BLOCKED,
                reason="Multiple inappropriate patterns detected",
                details={"matched_patterns": matched_patterns, "count": len(matched_patterns)},
                timestamp=datetime.utcnow()
            )
        
        if matched_patterns:
            return SafetyCheck(
                level=SafetyLevel.WARNING,
                reason="Suspicious content detected",
                details={"matched_patterns": matched_patterns},
                timestamp=datetime.utcnow()
            )
        
        return SafetyCheck(
            level=SafetyLevel.SAFE,
            reason="Content safety check passed",
            details={"matched_patterns": []},
            timestamp=datetime.utcnow()
        )
    
    def _check_pii(self, text: str) -> SafetyCheck:
        """Check for personally identifiable information"""
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
            r'\b\d{10,11}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        ]
        
        detected_pii = []
        for pattern in pii_patterns:
            if re.search(pattern, text):
                detected_pii.append(pattern)
        
        if detected_pii:
            return SafetyCheck(
                level=SafetyLevel.BLOCKED,
                reason="PII detected in message",
                details={"detected_pii": detected_pii},
                timestamp=datetime.utcnow()
            )
        
        return SafetyCheck(
            level=SafetyLevel.SAFE,
            reason="No PII detected",
            details={"detected_pii": []},
            timestamp=datetime.utcnow()
        )
    
    def _check_suspicious_activity(self, user_id: str, message: str) -> SafetyCheck:
        """Check for suspicious user activity patterns"""
        # Check for repeated similar messages
        user_requests = self.user_requests[user_id]
        recent_requests = [req for req in user_requests if datetime.utcnow() - req < timedelta(minutes=5)]
        
        if len(recent_requests) > 10:
            return SafetyCheck(
                level=SafetyLevel.BLOCKED,
                reason="Suspicious activity: too many requests in short time",
                details={"recent_requests": len(recent_requests)},
                timestamp=datetime.utcnow()
            )
        
        # Check for blocked users
        if user_id in self.blocked_users:
            return SafetyCheck(
                level=SafetyLevel.BLOCKED,
                reason="User is blocked",
                details={"user_id": user_id},
                timestamp=datetime.utcnow()
            )
        
        return SafetyCheck(
            level=SafetyLevel.SAFE,
            reason="No suspicious activity detected",
            details={"recent_requests": len(recent_requests)},
            timestamp=datetime.utcnow()
        )
    
    def _check_hallucination(self, response: str, original_query: str) -> SafetyCheck:
        """Basic hallucination detection"""
        # Check for common hallucination indicators
        hallucination_indicators = [
            "I don't have access to that information",
            "I cannot provide that information",
            "I'm not sure about that",
            "I don't know",
            "I cannot answer",
        ]
        
        response_lower = response.lower()
        for indicator in hallucination_indicators:
            if indicator.lower() in response_lower:
                return SafetyCheck(
                    level=SafetyLevel.WARNING,
                    reason="Potential hallucination detected",
                    details={"indicator": indicator},
                    timestamp=datetime.utcnow()
                )
        
        return SafetyCheck(
            level=SafetyLevel.SAFE,
            reason="No hallucination indicators detected",
            details={"indicators_found": []},
            timestamp=datetime.utcnow()
        )
    
    def _log_response(self, response: str, user_id: str, original_query: str):
        """Log response for monitoring"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "original_query": original_query,
            "response_length": len(response),
            "response_hash": hashlib.md5(response.encode()).hexdigest(),
        }
        
        self.response_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.response_log) > 1000:
            self.response_log = self.response_log[-1000:]
    
    def block_user(self, user_id: str, reason: str = "Manual block"):
        """Block a user from using the service"""
        self.blocked_users.add(user_id)
        logger.warning(f"User {user_id} blocked: {reason}")
    
    def unblock_user(self, user_id: str):
        """Unblock a user"""
        self.blocked_users.discard(user_id)
        logger.info(f"User {user_id} unblocked")
    
    def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety statistics"""
        return {
            "total_requests": sum(len(requests) for requests in self.user_requests.values()),
            "blocked_users": len(self.blocked_users),
            "flagged_responses": len(self.flagged_responses),
            "response_log_size": len(self.response_log),
            "rate_limits": self.rate_limits,
            "safety_thresholds": self.safety_thresholds,
        }
    
    def export_safety_log(self) -> str:
        """Export safety log for analysis"""
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "stats": self.get_safety_stats(),
            "blocked_users": list(self.blocked_users),
            "recent_responses": self.response_log[-100:],  # Last 100 responses
        }, indent=2) 