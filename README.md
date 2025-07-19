# AI Customer Support Agent - Project Structure

## Root Directory Structure

```
aven-ai-support/
├── backend/                    # Python FastAPI backend
├── frontend/                   # Next.js TypeScript frontend
├── shared/                     # Shared types and utilities
├── docker-compose.yml          # Local development setup
├── README.md
└── .env.example
```

## Backend Structure (Python/FastAPI)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment configuration
│   ├── database.py             # Database connections
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat endpoints
│   │   ├── search.py           # Search endpoints
│   │   ├── voice.py            # Voice processing
│   │   └── admin.py            # Admin/evaluation endpoints
│   │
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── ai_agent.py         # Main AI agent logic
│   │   ├── vector_store.py     # Vector database operations
│   │   ├── scraper.py          # Web scraping logic
│   │   ├── search_engine.py    # Real-time search
│   │   ├── guardrails.py       # Safety and content filtering
│   │   └── tools.py            # Tool calling (calendar, etc.)
│   │
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat-related models
│   │   ├── user.py             # User models
│   │   └── evaluation.py       # Evaluation models
│   │
│   ├── services/               # External service integrations
│   │   ├── __init__.py
│   │   ├── openai_service.py   # OpenAI API integration
│   │   ├── pinecone_service.py # Pinecone vector DB
│   │   ├── calendar_service.py # Calendar integration
│   │   └── scraping_service.py # Web scraping service
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── text_processing.py  # Text cleaning and processing
│   │   ├── embeddings.py       # Embedding generation
│   │   └── validators.py       # Input validation
│   │
│   └── websocket/              # WebSocket handlers
│       ├── __init__.py
│       ├── connection_manager.py
│       └── chat_handler.py
│
├── data/                       # Data and scraping
│   ├── scraped/                # Scraped content storage
│   ├── evaluation/             # Evaluation datasets
│   │   ├── questions.json      # Test questions
│   │   └── ground_truth.json   # Expected answers
│   └── processed/              # Processed data
│
├── scripts/                    # Utility scripts
│   ├── scrape_aven.py          # Initial scraping script
│   ├── setup_vector_db.py      # Vector DB initialization
│   ├── run_evaluation.py       # Evaluation runner
│   └── update_knowledge.py     # Knowledge update script
│
├── tests/                      # Test files
│   ├── __init__.py
│   ├── test_api/
│   ├── test_core/
│   └── test_services/
│
├── requirements.txt            # Python dependencies
├── Dockerfile
└── .env.example
```

## Frontend Structure (Next.js/TypeScript)

```
frontend/
├── src/
│   ├── app/                    # Next.js 13+ app router
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   ├── page.tsx            # Main chat page
│   │   ├── admin/              # Admin dashboard
│   │   │   └── page.tsx
│   │   └── api/                # API routes (if needed)
│   │       └── proxy/
│   │
│   ├── components/             # React components
│   │   ├── ui/                 # Base UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── card.tsx
│   │   │   └── modal.tsx
│   │   │
│   │   ├── chat/               # Chat-specific components
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── VoiceRecorder.tsx
│   │   │
│   │   ├── voice/              # Voice components
│   │   │   ├── VoiceChat.tsx
│   │   │   ├── AudioPlayer.tsx
│   │   │   └── VoiceControls.tsx
│   │   │
│   │   └── admin/              # Admin components
│   │       ├── EvaluationDashboard.tsx
│   │       ├── KnowledgeManager.tsx
│   │       └── Analytics.tsx
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useChat.ts          # Chat functionality
│   │   ├── useVoice.ts         # Voice recording/playback
│   │   ├── useWebSocket.ts     # WebSocket connection
│   │   └── useLocalStorage.ts  # Local storage management
│   │
│   ├── lib/                    # Utilities and configurations
│   │   ├── api.ts              # API client
│   │   ├── websocket.ts        # WebSocket client
│   │   ├── audio.ts            # Audio processing utilities
│   │   ├── openai-realtime.ts  # OpenAI Realtime API client
│   │   └── utils.ts            # General utilities
│   │
│   ├── store/                  # State management (Zustand)
│   │   ├── chatStore.ts        # Chat state
│   │   ├── userStore.ts        # User state
│   │   └── settingsStore.ts    # App settings
│   │
│   └── types/                  # TypeScript type definitions
│       ├── chat.ts             # Chat-related types
│       ├── voice.ts            # Voice-related types
│       ├── api.ts              # API response types
│       └── index.ts            # Exported types
│
├── public/                     # Static assets
│   ├── icons/
│   ├── sounds/                 # Audio files
│   └── images/
│
├── package.json
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
├── Dockerfile
└── .env.local.example
```

## Key Files Configuration

### Backend - requirements.txt
```
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
openai==1.3.7
pinecone-client==2.2.4
langchain==0.0.335
beautifulsoup4==4.12.2
playwright==1.40.0
redis==5.0.1
sqlalchemy==2.0.23
alembic==1.13.0
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2
numpy==1.24.3
pandas==2.1.4
scikit-learn==1.3.2
```

### Frontend - package.json (key dependencies)
```json
{
  "dependencies": {
    "next": "14.0.3",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.2",
    "@types/react": "18.2.42",
    "@types/react-dom": "18.2.17",
    "tailwindcss": "3.3.6",
    "zustand": "4.4.7",
    "socket.io-client": "4.7.4",
    "framer-motion": "10.16.16",
    "lucide-react": "0.294.0",
    "react-speech-kit": "3.0.1"
  }
}
```

### Docker Compose for Development
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/aven_ai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=aven_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Getting Started Commands

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Full Stack with Docker
```bash
docker-compose up --build
```

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
DATABASE_URL=postgresql://user:password@localhost:5432/aven_ai
REDIS_URL=redis://localhost:6379
GOOGLE_SEARCH_API_KEY=your_google_search_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_OPENAI_API_KEY=your_openai_key
```
