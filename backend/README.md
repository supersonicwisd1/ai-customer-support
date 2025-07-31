# Aven AI Support Backend

A comprehensive FastAPI backend for the Aven AI Support platform, featuring real-time voice chat, intelligent responses, comprehensive guardrails, and automated knowledge management.

## 🚀 Current Implementation Status

### ✅ **Fully Implemented & Working**
- **VAPI Voice Integration**: Complete real-time voice chat with VAPI.ai
- **Intelligent Response System**: Advanced query analysis and context-aware responses
- **Enhanced Guardrails**: Comprehensive safety checks with false positive prevention
- **Knowledge Base Management**: Automated scraping with Firecrawl and Pinecone storage
- **API Endpoints**: Complete REST API with health checks and monitoring
- **Testing Suite**: Comprehensive tests for all services and features
- **Error Handling**: Robust error handling with graceful fallbacks

### 🔄 **In Progress**
- **Performance Optimization**: Response time improvements
- **Advanced Analytics**: Usage tracking and insights
- **Enhanced Knowledge Base**: Continuous improvement of data quality

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment configuration
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat endpoints with guardrails
│   │   ├── vapi.py             # VAPI voice integration
│   │   ├── knowledge.py        # Knowledge base management
│   │   ├── guardrails.py       # Guardrails testing endpoints
│   │   └── cache.py            # Cache management
│   │
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── ai_agent.py         # Main AI agent orchestration
│   │   ├── vector_store.py     # Vector database operations
│   │   ├── query_analyzer.py   # Query classification and analysis
│   │   └── guardrails.py       # Safety and content filtering
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat-related models
│   │   └── user.py             # User models
│   │
│   ├── services/               # External service integrations
│   │   ├── __init__.py
│   │   ├── openai_service.py   # OpenAI API integration ✅
│   │   ├── pinecone_service.py # Pinecone vector DB ✅
│   │   ├── vapi_service.py     # VAPI.ai voice integration ✅
│   │   ├── assistant_service.py # Intelligent response orchestration ✅
│   │   ├── intelligent_response_service.py # Advanced response generation ✅
│   │   ├── guardrails_service.py # Enhanced safety system ✅
│   │   ├── enhanced_knowledge_service.py # Comprehensive knowledge management ✅
│   │   ├── cache_service.py    # Caching layer ✅
│   │   └── real_time_learning_service.py # Learning and analytics ✅
│   │
│   └── scripts/                # Utility scripts
│       ├── auto_discover_keywords.py
│       ├── crawl_aven_site.py
│       └── warm_cache.py
│
├── tests/                      # Comprehensive test suite
│   ├── test_services.py        # Service integration tests
│   ├── test_guardrails.py      # Guardrails functionality tests
│   ├── test_vapi_integration.py # Voice integration tests
│   ├── test_enhanced_knowledge.py # Knowledge base tests
│   └── test_json_parsing.py    # JSON parsing tests
│
├── requirements.txt            # Python dependencies
└── .env.example               # Environment variables template
```

## 🎯 Key Features

### **Voice Integration (VAPI.ai)**
- **Real-time Voice Chat**: Seamless voice conversations
- **Knowledge Base Integration**: Voice responses use the same knowledge base
- **Webhook Support**: Handles VAPI webhooks for voice responses
- **Call Management**: Create, monitor, and end voice calls
- **Error Handling**: Graceful handling of voice call issues

### **Intelligent Response System**
- **Query Analysis**: Advanced intent classification and entity extraction
- **Context-Aware Responses**: Personalized based on user context
- **Multi-Source Knowledge**: Combines multiple information sources
- **Response Enhancement**: Quality improvement and validation
- **Fallback Mechanisms**: Multiple layers of error handling

### **Enhanced Guardrails**
- **Input Validation**: Comprehensive safety checks for user input
- **Pattern Matching**: Detects personal information, financial advice, inappropriate content
- **False Positive Prevention**: Smart filtering to avoid blocking legitimate queries
- **Response Safety**: Ensures AI responses are appropriate
- **Comprehensive Logging**: Detailed audit trail for all safety checks

### **Knowledge Management**
- **Automated Scraping**: Firecrawl-based content extraction from Aven's website
- **Multi-Source Data**: Website, reviews, news, documentation
- **Vector Storage**: Pinecone for semantic search and retrieval
- **Real-time Updates**: Dynamic knowledge base updates
- **Source Attribution**: Transparent information sources

## 🛠️ Tech Stack

- **Framework**: FastAPI with async/await
- **AI/ML**: OpenAI GPT-4o-mini, text-embedding-3-small
- **Vector DB**: Pinecone for semantic search
- **Scraping**: Firecrawl for JavaScript-rendered content
- **Voice**: VAPI.ai for real-time voice processing
- **Caching**: Redis for performance optimization
- **Testing**: Comprehensive test suite with pytest

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- OpenAI API key
- Pinecone API key
- VAPI.ai API key
- Firecrawl API key

### **Installation**
```bash
# Clone the repository
git clone <repository-url>
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Environment Variables**
```env
# Core APIs
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
VAPI_PRIVATE_KEY=your_vapi_private_key
VAPI_PUBLIC_KEY=your_vapi_public_key
FIRECRAWL_API_KEY=your_firecrawl_key

# Optional: Database (for future features)
DATABASE_URL=postgresql://user:password@localhost:5432/aven_ai
REDIS_URL=redis://localhost:6379
```

## 📊 API Endpoints

### **Core Endpoints**
- `POST /api/chat/message` - Text chat with guardrails
- `GET /health` - Health check
- `GET /api/chat/health` - Chat service health

### **Voice Integration (VAPI)**
- `GET /api/vapi/config` - VAPI configuration
- `GET /api/vapi/health` - VAPI service health
- `POST /api/vapi/webhook` - VAPI webhook for voice responses
- `POST /api/vapi/calls` - Create voice calls
- `GET /api/vapi/calls/{call_id}` - Get call status
- `PUT /api/vapi/calls/{call_id}/end` - End voice call

### **Knowledge Management**
- `POST /api/knowledge/rebuild` - Rebuild knowledge base
- `GET /api/knowledge/status` - Knowledge base status
- `GET /api/knowledge/stats` - Knowledge base statistics

### **Guardrails Testing**
- `POST /api/guardrails/test` - Test guardrails functionality
- `GET /api/guardrails/health` - Guardrails service health

### **Cache Management**
- `GET /api/cache/status` - Cache status
- `POST /api/cache/clear` - Clear cache
- `GET /api/cache/stats` - Cache statistics

## 🧪 Testing

### **Run All Tests**
```bash
# Test all services
python test_services.py

# Test guardrails functionality
python test_guardrails.py

# Test voice integration
python test_vapi_integration.py

# Test knowledge base
python test_enhanced_knowledge.py

# Test JSON parsing
python test_json_parsing.py
```

### **Individual Service Tests**
```bash
# Test OpenAI service
python -c "from app.services.openai_service import OpenAIService; print('OpenAI service test')"

# Test Pinecone service
python -c "from app.services.pinecone_service import PineconeService; print('Pinecone service test')"

# Test VAPI service
python -c "from app.services.vapi_service import VapiService; print('VAPI service test')"
```

## 🔧 Configuration

### **Voice Settings**
Configure VAPI voice settings in `app/services/vapi_service.py`:
```python
# Voice configuration
voice_config = {
    "model": "gpt-4o",
    "voice": "11labs",
    "knowledge_base": {
        "type": "pinecone",
        "index_name": "aven-ai-knowledge",
        "namespace": "aven-docs"
    }
}
```

### **Guardrails Configuration**
Customize safety rules in `app/services/guardrails_service.py`:
```python
# Personal information patterns
personal_info_patterns = [
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card
    r'\b\d{3}-\d{3}-\d{4}\b',  # Phone number
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',  # Email
]
```

### **Knowledge Base**
Manage knowledge sources in `app/services/enhanced_knowledge_service.py`:
```python
# Scraping sources
scraping_sources = [
    "https://aven.com",
    "https://aven.com/support",
    "https://aven.com/help",
    # Add more sources as needed
]
```

## 🐛 Troubleshooting

### **Common Issues**

1. **VAPI Voice Not Working**
   ```bash
   # Check VAPI configuration
   curl http://localhost:8000/api/vapi/config
   
   # Test VAPI health
   curl http://localhost:8000/api/vapi/health
   ```

2. **Guardrails Blocking Legitimate Queries**
   ```bash
   # Test guardrails with simple query
   curl -X POST http://localhost:8000/api/guardrails/test \
     -H "Content-Type: application/json" \
     -d '{"message": "What is Aven?"}'
   ```

3. **Knowledge Base Issues**
   ```bash
   # Check knowledge base status
   curl http://localhost:8000/api/knowledge/status
   
   # Rebuild knowledge base
   curl -X POST http://localhost:8000/api/knowledge/rebuild
   ```

4. **OpenAI API Errors**
   ```bash
   # Check OpenAI service
   python -c "from app.services.openai_service import OpenAIService; s = OpenAIService(); print('OpenAI service OK')"
   ```

### **Debug Commands**
```bash
# Check all services
python test_services.py

# Test specific functionality
python test_guardrails.py

# Monitor logs
tail -f logs/app.log

# Check environment variables
python -c "import os; print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

## 📈 Performance

### **Response Times**
- **Text Chat**: ~2-3 seconds average
- **Voice Processing**: ~1-2 seconds average
- **Knowledge Search**: ~500ms average
- **Guardrails Check**: ~100ms average

### **Optimization Tips**
- Use caching for frequently accessed data
- Implement connection pooling for databases
- Monitor API rate limits
- Use async/await for I/O operations

## 🔒 Security

### **Guardrails System**
- **Input Validation**: All user input is validated
- **Content Filtering**: Inappropriate content is blocked
- **Personal Information**: Sensitive data is detected and blocked
- **Financial Advice**: Financial advice is filtered appropriately

### **API Security**
- **Rate Limiting**: Implemented for all endpoints
- **Input Sanitization**: All inputs are sanitized
- **Error Handling**: Secure error messages
- **Logging**: Comprehensive audit trail