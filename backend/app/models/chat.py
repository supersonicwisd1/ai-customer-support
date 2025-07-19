from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class QueryType(str, Enum):
    GENERAL = "general"
    REALTIME = "realtime"
    KNOWLEDGE_BASE = "knowledge_base"
    MEETING = "meeting"

class SafetyLevel(str, Enum):
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"
    CRITICAL = "critical"

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session identifier")
    include_sources: bool = Field(True, description="Whether to include sources in response")

class ChatResponse(BaseModel):
    message: str = Field(..., description="AI's response message")
    sources: List[str] = Field(default_factory=list, description="Source URLs")
    confidence: float = Field(..., description="Confidence score (0-1)")
    session_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: str = Field(..., description="Response timestamp")
    processing_time: float = Field(..., description="Processing time in seconds")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    safety_level: str = Field("safe", description="Safety level of the response")
    safety_reason: Optional[str] = Field(None, description="Reason for safety level")

class ChatSession(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    message_count: int = Field(0, description="Number of messages in session")
    is_active: bool = Field(True, description="Whether session is active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")

class SearchQuery(BaseModel):
    query: str = Field(..., description="Search query")
    max_results: int = Field(5, description="Maximum number of results")
    include_sources: bool = Field(True, description="Whether to include sources")

class SearchResult(BaseModel):
    title: str = Field(..., description="Result title")
    content: str = Field(..., description="Result content")
    url: str = Field(..., description="Result URL")
    source: str = Field(..., description="Source type")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    timestamp: datetime = Field(..., description="Result timestamp")

class VoiceChatRequest(BaseModel):
    audio_data: bytes = Field(..., description="Audio data")
    session_id: Optional[str] = Field(None, description="Session identifier")
    voice: str = Field("alloy", description="Voice to use for response")

class VoiceChatResponse(BaseModel):
    transcription: str = Field(..., description="Transcribed text")
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session identifier")
    confidence: float = Field(..., description="Confidence score")
    sources: List[str] = Field(default_factory=list, description="Source URLs")
    audio_url: Optional[str] = Field(None, description="Audio response URL")
    safety_level: str = Field("safe", description="Safety level")
    safety_reason: Optional[str] = Field(None, description="Safety reason")

class SafetyCheck(BaseModel):
    level: SafetyLevel = Field(..., description="Safety level")
    reason: str = Field(..., description="Reason for safety level")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    timestamp: datetime = Field(..., description="Check timestamp")

class GuardrailsStats(BaseModel):
    total_requests: int = Field(..., description="Total requests processed")
    blocked_users: int = Field(..., description="Number of blocked users")
    flagged_responses: int = Field(..., description="Number of flagged responses")
    response_log_size: int = Field(..., description="Size of response log")
    rate_limits: Dict[str, int] = Field(..., description="Rate limit settings")
    safety_thresholds: Dict[str, Any] = Field(..., description="Safety threshold settings") 
