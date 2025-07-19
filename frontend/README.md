# Aven AI Support Frontend

A modern, responsive AI customer support chat interface for Aven (aven.com) built with Next.js 14, TypeScript, and Tailwind CSS.

## 🚀 Features

### Core Functionality
- **AI-Powered Chat**: Real-time conversation with OpenAI-powered assistant
- **Voice Chat**: Record and send voice messages with transcription
- **Text-to-Speech**: AI responses can be played as audio
- **Source Attribution**: View sources and links for AI responses
- **Session Management**: Persistent chat sessions across conversations

### User Interface
- **Modern Design**: Clean, ChatGPT-inspired interface
- **Dark/Light Mode**: Toggle between themes
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Feedback**: Loading states, typing indicators, and animations
- **Accessibility**: Keyboard navigation and screen reader support

### Advanced Features
- **Voice Settings**: Choose from multiple AI voices
- **Response Length**: Configure short, medium, or long responses
- **Source Display**: Toggle source attribution on/off
- **Auto-play Audio**: Automatically play AI voice responses
- **Error Handling**: Graceful error handling with user-friendly messages

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Audio**: Web Audio API, MediaRecorder API

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running (FastAPI server)

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
```

### 2. Environment Configuration

Create a `.env.local` file in the root directory:

```env
# Aven AI Support Frontend Environment Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Override for production
# NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

### 3. Start Development Server

```bash
# Start the development server
npm run dev
```

The application will be available at `http://localhost:3000`

### 4. Build for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout with metadata
│   │   ├── page.tsx           # Main page component
│   │   └── globals.css        # Global styles and Tailwind
│   ├── components/            # React components
│   │   ├── ChatContainer.tsx  # Main chat interface
│   │   ├── ChatInput.tsx      # Text input and voice recorder
│   │   ├── Message.tsx        # Individual message display
│   │   ├── VoiceRecorder.tsx  # Voice recording functionality
│   │   └── Settings.tsx       # Settings modal
│   ├── lib/                   # Utility libraries
│   │   └── api.ts            # API client for backend
│   ├── store/                 # State management
│   │   └── chatStore.ts      # Zustand store for chat state
│   └── types/                 # TypeScript type definitions
│       └── chat.ts           # Chat-related types
├── public/                    # Static assets
├── package.json              # Dependencies and scripts
├── tailwind.config.ts        # Tailwind configuration
└── tsconfig.json            # TypeScript configuration
```

## 🔧 Configuration

### Backend API Endpoints

The frontend expects the following API endpoints from your backend:

- `POST /api/chat/text` - Text chat
- `POST /api/voice/chat` - Voice chat
- `POST /api/voice/synthesize` - Text-to-speech
- `GET /api/voice/voices` - Available voices
- `GET /health` - Health check
- `GET /api/voice/health` - Voice service health

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

## 🎨 Customization

### Styling

The application uses Tailwind CSS for styling. You can customize:

- **Colors**: Modify the color palette in `tailwind.config.ts`
- **Fonts**: Update font families in `src/app/layout.tsx`
- **Components**: Edit component styles in individual files

### Branding

To customize for your brand:

1. Update the title and description in `src/app/layout.tsx`
2. Replace the logo in the header (`src/components/ChatContainer.tsx`)
3. Update the welcome message and suggestions
4. Modify the color scheme to match your brand

### Features

You can enable/disable features by:

- **Voice Chat**: Set `voiceAvailable` in the store
- **Source Display**: Toggle in settings
- **Auto-play Audio**: Configure in settings
- **Response Length**: Adjust in settings

## 🔍 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure your backend is running on the correct port
   - Check the `NEXT_PUBLIC_API_URL` environment variable
   - Verify CORS settings on your backend

2. **Voice Recording Not Working**
   - Check microphone permissions in your browser
   - Ensure HTTPS in production (required for MediaRecorder)
   - Verify the voice service is available

3. **Build Errors**
   - Clear `.next` directory: `rm -rf .next`
   - Reinstall dependencies: `npm install`
   - Check TypeScript errors: `npm run lint`

### Development Tips

- Use the browser's developer tools to debug API calls
- Check the Network tab for failed requests
- Use the Console for error messages
- Test voice features in Chrome/Edge (best MediaRecorder support)

## 📱 Browser Support

- **Chrome**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support (iOS 14.3+)
- **Edge**: Full support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- Check the troubleshooting section above
- Review the backend API documentation
- Open an issue on GitHub

---

**Built with ❤️ for Aven AI Support**
