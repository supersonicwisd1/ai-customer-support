# Aven AI Support Frontend

A modern, responsive AI customer support chat interface for Aven (aven.com) built with Next.js 14, TypeScript, and Tailwind CSS, featuring real-time voice chat with VAPI.ai integration.

## 🚀 Features

### Core Functionality
- **AI-Powered Chat**: Real-time conversation with OpenAI-powered assistant
- **VAPI Voice Integration**: Seamless real-time voice chat with VAPI.ai
- **Enhanced Message Display**: Beautiful markdown support with numbered lists and links
- **Resizable Chat Widget**: Drag-to-resize interface for optimal user experience
- **Source Attribution**: View sources and links for AI responses
- **Session Management**: Persistent chat sessions across conversations

### User Interface
- **Modern Design**: Clean, ChatGPT-inspired interface with professional styling
- **Dark/Light Mode**: Toggle between themes with smooth transitions
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Real-time Feedback**: Loading states, typing indicators, and smooth animations
- **Accessibility**: Keyboard navigation and screen reader support
- **Resizable Widget**: Drag the corner to resize the chat interface

### Advanced Features
- **Voice Call Management**: In-app voice calls without popups or new tabs
- **Enhanced Message Formatting**: Support for bold text, links, and numbered lists
- **Error Suppression**: Handles audio processor warnings gracefully
- **Guardrails Integration**: Real-time safety checks with user-friendly error messages
- **Auto-scroll**: Smooth scrolling to latest messages
- **Message Status**: Visual indicators for message states (sending, sent, error)

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: Zustand
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Voice SDK**: @vapi-ai/web for real-time voice integration

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running (FastAPI server with VAPI integration)

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
│   │   ├── QuickChatWidget.tsx # Main resizable chat widget
│   │   ├── ChatInterface.tsx  # Chat interface with voice integration
│   │   ├── Message.tsx        # Enhanced message display with markdown
│   │   ├── VapiVoiceWidget.tsx # VAPI voice integration component
│   │   └── BackendStatus.tsx  # Backend health monitoring
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

- `POST /api/chat/message` - Text chat with guardrails
- `GET /api/vapi/config` - VAPI configuration
- `GET /api/vapi/health` - VAPI service health
- `POST /api/vapi/webhook` - VAPI webhook for voice responses
- `GET /health` - Health check

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
- **Chat Widget**: Customize the resizable widget in `QuickChatWidget.tsx`

### Branding

To customize for your brand:

1. Update the title and description in `src/app/layout.tsx`
2. Replace the logo in the header (`src/components/ChatInterface.tsx`)
3. Update the welcome message and suggestions
4. Modify the color scheme to match your brand
5. Customize the chat widget appearance

### Features

You can enable/disable features by:

- **Voice Chat**: Configure VAPI settings in the backend
- **Resizable Widget**: Modify resize constraints in `QuickChatWidget.tsx`
- **Message Formatting**: Adjust markdown support in `Message.tsx`
- **Animations**: Customize Framer Motion animations

## 🔍 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure your backend is running on the correct port
   - Check the `NEXT_PUBLIC_API_URL` environment variable
   - Verify CORS settings on your backend
   - Check the browser console for network errors

2. **Voice Call Not Working**
   - Check VAPI API keys in the backend
   - Verify microphone permissions in your browser
   - Ensure HTTPS in production (required for MediaRecorder)
   - Check browser console for VAPI SDK errors
   - Verify the voice service is available via `/api/vapi/health`

3. **Message Formatting Issues**
   - Check that markdown is being parsed correctly
   - Verify the `Message.tsx` component is handling formatting
   - Test with simple messages first

4. **Resizable Widget Issues**
   - Check that the resize handle is visible
   - Verify mouse events are being captured
   - Test on different screen sizes

5. **Build Errors**
   - Clear `.next` directory: `rm -rf .next`
   - Reinstall dependencies: `npm install`
   - Check TypeScript errors: `npm run lint`
   - Verify all imports are correct

### Development Tips

- Use the browser's developer tools to debug API calls
- Check the Network tab for failed requests
- Use the Console for error messages
- Test voice features in Chrome/Edge (best MediaRecorder support)
- Monitor the browser's Application tab for storage issues

## 📱 Browser Support

- **Chrome**: Full support (recommended for voice features)
- **Firefox**: Full support
- **Safari**: Full support (iOS 14.3+)
- **Edge**: Full support

### Voice Feature Compatibility
- **Chrome**: Best support for VAPI voice integration
- **Firefox**: Good support, some audio processor warnings
- **Safari**: Limited support for advanced voice features
- **Mobile**: iOS Safari has limited voice support

## 🎯 Key Features in Detail

### **Enhanced Chat Display**
- **Markdown Support**: Bold text (`**text**`), links (`[text](url)`), numbered lists
- **Responsive Design**: Adapts to different screen sizes with proper text wrapping
- **Message Formatting**: Professional styling with proper spacing and typography
- **Loading States**: Visual feedback during message processing
- **Error Handling**: Graceful error messages with retry options

### **VAPI Voice Integration**
- **Real-time Voice**: Seamless voice conversations without popups
- **In-app Calls**: Voice calls integrated directly into the chat interface
- **Error Suppression**: Handles audio processor warnings gracefully
- **Call Management**: Start, stop, and monitor voice calls
- **Voice Settings**: Configurable voice options through VAPI

### **Resizable Chat Widget**
- **Drag-to-Resize**: Click and drag the corner to resize the widget
- **Size Constraints**: Minimum and maximum size limits
- **Smooth Animations**: Framer Motion animations for resize
- **Responsive**: Adapts to different screen sizes
- **Persistent**: Remembers size preferences

### **Guardrails Integration**
- **Real-time Validation**: Checks user input for safety
- **User-friendly Messages**: Clear error messages for blocked content
- **Graceful Handling**: Continues working even when guardrails are triggered
- **Visual Feedback**: Shows when messages are blocked

## 🔧 Advanced Configuration

### **VAPI Voice Settings**
Configure voice settings in the backend:
```javascript
// VAPI configuration
const vapiConfig = {
  apiKey: process.env.VAPI_API_KEY,
  assistantId: process.env.VAPI_ASSISTANT_ID,
  voice: "11labs",
  language: "en"
};
```

### **Chat Widget Customization**
Modify the resizable widget in `QuickChatWidget.tsx`:
```typescript
// Size constraints
const MIN_SIZE = { width: 320, height: 400 };
const MAX_SIZE = { width: 600, height: 800 };
const DEFAULT_SIZE = { width: 400, height: 600 };
```

### **Message Formatting**
Customize markdown support in `Message.tsx`:
```typescript
// Supported markdown features
const markdownFeatures = {
  bold: /\*\*(.*?)\*\*/g,
  links: /\[(.*?)\]\((.*?)\)/g,
  lists: /^\d+\.\s/g
};
```