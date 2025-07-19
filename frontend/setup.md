# Setup Instructions

## Environment Configuration

1. Create a `.env.local` file in the root directory:

```bash
# Aven AI Support Frontend Environment Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Override for production
# NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

2. Make sure your backend is running on the specified URL

3. Start the development server:

```bash
npm run dev
```

## Backend Requirements

Your backend should provide these endpoints:

- `POST /api/chat/text` - Text chat
- `POST /api/voice/chat` - Voice chat  
- `POST /api/voice/synthesize` - Text-to-speech
- `GET /api/voice/voices` - Available voices
- `GET /health` - Health check
- `GET /api/voice/health` - Voice service health

## Browser Requirements

For voice features to work:
- HTTPS required in production
- Microphone permissions needed
- Chrome/Edge recommended for best compatibility 