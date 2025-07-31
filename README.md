# Aven AI Support - AI-Powered Customer Support Platform

A comprehensive AI-powered customer support platform for Aven (aven.com) featuring real-time voice chat, intelligent responses, and comprehensive knowledge management.

## 🚀 Current Status

### ✅ **Fully Implemented & Working**
- **VAPI Voice Integration**: Real-time voice chat with VAPI.ai
- **Enhanced Chat Interface**: Beautiful, responsive chat with markdown support
- **Intelligent Response System**: Advanced query analysis and context-aware responses
- **Comprehensive Guardrails**: Safety checks for user input with false positive prevention
- **Knowledge Base Management**: Automated scraping and vector storage
- **Frontend Enhancements**: Resizable chat widget, improved message display
- **Backend Services**: All core services operational and tested

### 🔄 **In Progress**
- **Enhanced Knowledge Base**: Continuous improvement of scraped data quality
- **Performance Optimization**: Response time improvements
- **Advanced Analytics**: Usage tracking and insights

## 🏗️ Project Structure

```
aven-ai-support/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints (chat, vapi, knowledge)
│   │   ├── services/          # Core services (OpenAI, Pinecone, Guardrails)
│   │   ├── core/              # Business logic
│   │   └── models/            # Data models
│   ├── tests/                 # Comprehensive test suite
│   └── requirements.txt       # Python dependencies
├── frontend/                  # Next.js TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── store/            # Zustand state management
│   │   └── lib/              # Utilities and API client
│   └── package.json          # Frontend dependencies
└── README.md                 # This file
```

## 🎯 Key Features

### **Voice & Chat Integration**
- **VAPI.ai Integration**: Seamless real-time voice conversations
- **Text Chat**: Full-featured text chat with markdown support
- **Resizable Widget**: Drag-to-resize chat interface
- **Voice Call Management**: In-app voice calls without popups

### **Intelligent AI Responses**
- **Query Analysis**: Advanced intent classification and entity extraction
- **Context-Aware Responses**: Personalized based on user context
- **Knowledge Base Integration**: Real-time information from Aven's website
- **Multi-Source Retrieval**: Combines multiple information sources

### **Safety & Compliance**
- **Enhanced Guardrails**: Comprehensive content filtering
- **False Positive Prevention**: Smart pattern matching
- **User Input Validation**: Real-time safety checks
- **Response Quality Control**: Ensures appropriate content

### **Knowledge Management**
- **Automated Scraping**: Firecrawl-based content extraction
- **Vector Database**: Pinecone for semantic search
- **Real-time Updates**: Dynamic knowledge base updates
- **Source Attribution**: Transparent information sources

## 🛠️ Tech Stack

### **Backend**
- **Framework**: FastAPI with async/await
- **AI/ML**: OpenAI GPT-4o-mini, text-embedding-3-small
- **Vector DB**: Pinecone for semantic search
- **Scraping**: Firecrawl for JavaScript-rendered content
- **Voice**: VAPI.ai for real-time voice processing
- **Testing**: Comprehensive test suite

### **Frontend**
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: Zustand
- **Animations**: Framer Motion
- **Voice SDK**: @vapi-ai/web

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- Node.js 18+
- OpenAI API key
- Pinecone API key
- VAPI.ai API key
- Firecrawl API key

### **Backend Setup**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Frontend Setup**
```bash
cd frontend
npm install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your backend URL

# Start the development server
npm run dev
```

### **Environment Variables**

#### **Backend (.env)**
```env
# Core APIs
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
VAPI_PRIVATE_KEY=your_vapi_private_key
VAPI_PUBLIC_KEY=your_vapi_public_key
FIRECRAWL_API_KEY=your_firecrawl_key
```

#### **Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Testing

### **Backend Tests**
```bash
cd backend
python test_services.py          # Test all services
python test_guardrails.py        # Test safety features
python test_vapi_integration.py  # Test voice integration
```

### **Frontend Tests**
```bash
cd frontend
npm test
```

## 📊 API Endpoints

### **Core Endpoints**
- `POST /api/chat/message` - Text chat with guardrails
- `GET /api/vapi/config` - VAPI configuration
- `POST /api/vapi/webhook` - VAPI webhook for voice responses
- `POST /api/knowledge/rebuild` - Rebuild knowledge base
- `GET /health` - Health check

### **Voice Integration**
- `GET /api/vapi/health` - VAPI service health
- `POST /api/vapi/calls` - Create voice calls
- `GET /api/vapi/calls/{call_id}` - Get call status

## 🎨 Features in Detail

### **Enhanced Chat Display**
- **Markdown Support**: Bold text, links, numbered lists
- **Responsive Design**: Adapts to different screen sizes
- **Message Formatting**: Professional styling with proper spacing
- **Loading States**: Visual feedback during processing
- **Error Handling**: Graceful error messages

### **Voice Integration**
- **Real-time Voice**: Seamless voice conversations
- **No Popups**: In-app voice calls
- **Voice Settings**: Configurable voice options
- **Call Management**: Start, stop, and monitor calls
- **Error Suppression**: Handles audio processor warnings

### **Guardrails System**
- **Input Validation**: Checks user messages for safety
- **Pattern Matching**: Detects personal information, financial advice
- **False Positive Prevention**: Smart filtering to avoid blocking legitimate queries
- **Response Safety**: Ensures AI responses are appropriate
- **Comprehensive Logging**: Detailed audit trail

### **Knowledge Management**
- **Automated Scraping**: Firecrawl-based content extraction
- **Multi-Source Data**: Website, reviews, news, documentation
- **Vector Storage**: Pinecone for semantic search
- **Real-time Updates**: Dynamic knowledge base
- **Source Attribution**: Transparent information sources

## 🔧 Configuration

### **Voice Settings**
Configure VAPI voice settings in the backend:
- Voice type (11labs, etc.)
- Language settings
- Call parameters

### **Guardrails Configuration**
Customize safety rules in `backend/app/services/guardrails_service.py`:
- Personal information patterns
- Financial advice keywords
- Brand safety rules
- Inappropriate content filters

### **Knowledge Base**
Manage knowledge sources in `backend/app/services/enhanced_knowledge_service.py`:
- Scraping sources
- Content processing
- Vector storage settings

## 🐛 Troubleshooting

### **Common Issues**

1. **Voice Call Not Working**
   - Check VAPI API keys
   - Verify microphone permissions
   - Check browser console for errors

2. **Guardrails Blocking Legitimate Queries**
   - Check guardrails logs
   - Verify pattern matching
   - Test with simple queries

3. **Knowledge Base Issues**
   - Run knowledge rebuild: `POST /api/knowledge/rebuild`
   - Check Pinecone connection
   - Verify scraping sources

4. **Frontend Connection Issues**
   - Check `NEXT_PUBLIC_API_URL`
   - Verify backend is running
   - Check CORS settings

### **Debug Commands**
```bash
# Test backend services
cd backend && python test_services.py

# Test guardrails
python test_guardrails.py

# Test voice integration
python test_vapi_integration.py

# Check knowledge base
curl http://localhost:8000/api/knowledge/status
```