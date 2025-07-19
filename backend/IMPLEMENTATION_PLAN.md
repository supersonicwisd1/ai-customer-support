# Aven AI Customer Support Agent - Implementation Plan

## Current Status Analysis

### ✅ Completed Components
- **FastAPI Backend**: Basic structure with CORS, health checks, WebSocket support
- **Services Layer**: 
  - `OpenAIService`: Chat and embeddings generation (working)
  - `PineconeService`: Vector database operations (working)
  - `EnhancedScrapingService`: Firecrawl-based web scraping (working)
- **Configuration**: Environment-based settings with Pydantic
- **Testing**: Comprehensive test suite for all services
- **Basic Endpoints**: Root, health, chat (echo), WebSocket

### 🔄 Missing Components
- **API Routes**: No structured API endpoints in `/app/api/`
- **Database Models**: Empty `database.py`
- **Core Business Logic**: No AI agent orchestration
- **Real-time Search**: No search service implementation
- **Voice Processing**: No voice endpoints or services
- **Guardrails**: No content filtering or safety measures
- **Tool Calling**: No calendar or meeting scheduling
- **Evaluation System**: No evaluation framework

## Implementation Phases

### Phase 1: Core AI Agent & Chat Interface
**Priority: High | Complexity: Medium**

#### 1.1 Create API Routes Structure
```
app/api/
├── __init__.py
├── chat.py              # Text chat endpoints
├── search.py            # Real-time search endpoints
├── voice.py             # Voice chat endpoints
├── calendar.py          # Meeting scheduling endpoints
└── evaluation.py        # Evaluation endpoints
```

#### 1.2 Implement Core AI Agent
```
app/core/
├── __init__.py
├── ai_agent.py          # Main AI agent orchestration
├── vector_store.py      # Vector database operations wrapper
├── search_engine.py     # Real-time search integration
├── guardrails.py        # Safety and content filtering
└── tools.py             # Tool calling (calendar, etc.)
```

#### 1.3 Create Data Models
```
app/models/
├── __init__.py
├── chat.py              # Chat-related models
├── user.py              # User models
├── evaluation.py        # Evaluation models
└── calendar.py          # Calendar/meeting models
```

### Phase 2: Real-time Search Integration
**Priority: High | Complexity: Medium**

#### 2.1 Implement Search Service
```python
# app/services/search_service.py
class SearchService:
    - Google Custom Search API integration
    - Query classification for "latest/current" keywords
    - Search result processing and formatting
    - Integration with existing knowledge base
```

#### 2.2 Create Query Analyzer
```python
# app/core/query_analyzer.py
class QueryAnalyzer:
    - Detect real-time search keywords
    - Classify query types (general vs current info)
    - Route queries to appropriate services
```

### Phase 3: Voice Chat Integration
**Priority: Medium | Complexity: High**

#### 3.1 Voice Service Implementation
```python
# app/services/voice_service.py
class VoiceService:
    - OpenAI Realtime API integration
    - Audio processing and streaming
    - Voice-to-text and text-to-voice
```

#### 3.2 WebSocket Voice Handler
```python
# app/websocket/voice_handler.py
class VoiceWebSocketHandler:
    - Real-time audio streaming
    - WebRTC integration
    - Voice chat session management
```

### Phase 4: Safety & Guardrails
**Priority: High | Complexity: Medium**

#### 4.1 Content Filtering
```python
# app/core/guardrails.py
class Guardrails:
    - Personal data detection
    - Legal/financial advice filtering
    - Toxicity detection
    - Response validation
```

#### 4.2 Safety Measures
- OpenAI Moderation API integration
- Response sanitization
- User input validation
- Rate limiting

### Phase 5: Tool Calling & Calendar Integration
**Priority: Medium | Complexity: Medium**

#### 5.1 Calendar Service
```python
# app/services/calendar_service.py
class CalendarService:
    - Google Calendar API integration
    - Meeting scheduling logic
    - Date/time parsing and validation
```

#### 5.2 Tool Calling Framework
```python
# app/core/tools.py
class ToolCallingFramework:
    - Tool registration and execution
    - Meeting scheduling orchestration
    - Tool response formatting
```

### Phase 6: Evaluation System
**Priority: Low | Complexity: Medium**

#### 6.1 Evaluation Framework
```python
# app/evaluation/
├── __init__.py
├── evaluator.py         # Main evaluation logic
├── metrics.py           # Accuracy, helpfulness, citation metrics
├── dataset.py           # Test question management
└── dashboard.py         # Evaluation results display
```

#### 6.2 Test Dataset
- 50 realistic user questions
- Ground truth answers
- Evaluation criteria
- Automated scoring system

## Technical Implementation Details

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    session_id TEXT UNIQUE,
    created_at TIMESTAMP,
    last_active TIMESTAMP
);

-- Chat sessions table
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    session_type TEXT, -- 'text' or 'voice'
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Messages table
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    role TEXT, -- 'user' or 'assistant'
    content TEXT,
    sources JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- Evaluations table
CREATE TABLE evaluations (
    id INTEGER PRIMARY KEY,
    question TEXT,
    expected_answer TEXT,
    actual_answer TEXT,
    accuracy_score FLOAT,
    helpfulness_score FLOAT,
    citation_score FLOAT,
    created_at TIMESTAMP
);
```

### API Endpoints Structure

#### Chat Endpoints
```python
POST /api/chat/text          # Text chat
POST /api/chat/voice         # Voice chat
GET  /api/chat/history       # Chat history
DELETE /api/chat/session     # Clear session
```

#### Search Endpoints
```python
POST /api/search/query       # Real-time search
GET  /api/search/history     # Search history
POST /api/search/analyze     # Query analysis
```

#### Calendar Endpoints
```python
POST /api/calendar/schedule  # Schedule meeting
GET  /api/calendar/available # Check availability
DELETE /api/calendar/cancel  # Cancel meeting
```

#### Evaluation Endpoints
```python
POST /api/evaluation/run     # Run evaluation
GET  /api/evaluation/results # Get results
POST /api/evaluation/feedback # User feedback
```

### WebSocket Events
```javascript
// Client to Server
{
  "type": "chat_message",
  "data": { "message": "What is Aven?" }
}

{
  "type": "voice_start",
  "data": { "session_id": "abc123" }
}

{
  "type": "voice_audio",
  "data": { "audio": "base64_encoded_audio" }
}

// Server to Client
{
  "type": "chat_response",
  "data": { 
    "message": "Aven is a financial technology company...",
    "sources": ["https://aven.com/about"],
    "confidence": 0.95
  }
}

{
  "type": "voice_response",
  "data": { "audio": "base64_encoded_response" }
}
```

## Environment Variables Required

```bash
# Existing
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
FIRECRAWL_API_KEY=your_firecrawl_key

# New Required
GOOGLE_SEARCH_API_KEY=your_google_search_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
GOOGLE_CALENDAR_CLIENT_ID=your_google_client_id
GOOGLE_CALENDAR_CLIENT_SECRET=your_google_client_secret
GOOGLE_CALENDAR_REFRESH_TOKEN=your_refresh_token

# Optional
SERPAPI_KEY=your_serpapi_key  # Alternative to Google Search
CALENDLY_API_KEY=your_calendly_key  # Alternative to Google Calendar
```

## Dependencies to Add

```bash
# Search
pip install google-api-python-client google-auth google-auth-oauthlib

# Calendar
pip install google-auth-httplib2

# Voice (if using OpenAI Realtime)
pip install openai-realtime

# Database
pip install sqlalchemy alembic

# Additional utilities
pip install python-multipart python-jose[cryptography] passlib[bcrypt]
```

## Testing Strategy

### Unit Tests
- Service layer testing (OpenAI, Pinecone, Search, Calendar)
- Core logic testing (AI agent, guardrails, tools)
- Model validation testing

### Integration Tests
- API endpoint testing
- WebSocket testing
- Database integration testing
- End-to-end workflow testing

### Evaluation Tests
- Automated evaluation with test dataset
- Performance benchmarking
- Accuracy and helpfulness scoring

## Deployment Considerations

### Development
- Local development with hot reload
- Environment variable management
- Database migrations with Alembic

### Production
- Docker containerization
- Environment-specific configurations
- Database backup and recovery
- Monitoring and logging
- Rate limiting and security

## Success Metrics

### Technical Metrics
- API response time < 2 seconds
- WebSocket connection stability > 99%
- Vector search accuracy > 90%
- Real-time search relevance > 85%

### User Experience Metrics
- Chat response accuracy > 90%
- Voice recognition accuracy > 95%
- Meeting scheduling success rate > 95%
- User satisfaction score > 4.5/5

### Business Metrics
- Query resolution rate > 85%
- User engagement time > 5 minutes
- Meeting conversion rate > 30%
- Support ticket reduction > 40% 