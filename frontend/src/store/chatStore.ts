import { create } from 'zustand';
import { apiClient } from '@/lib/api';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string;
  status: 'sending' | 'sent' | 'error';
  isVoiceMessage?: boolean;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  sessionId: string | null;
  error: string | null;
  
  // VAPI state
  vapiConnected: boolean;
  vapiCallId: string | null;
  
  // Actions
  sendMessage: (content: string) => Promise<void>;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  clearMessages: () => void;
  setSessionId: (sessionId: string) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // VAPI actions
  setVapiConnected: (connected: boolean) => void;
  setVapiCallId: (callId: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  sessionId: null,
  error: null,
  vapiConnected: false,
  vapiCallId: null,

  sendMessage: async (content: string) => {
    const { addMessage, updateMessage, setError, clearError } = get();
    
    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date().toISOString(),
      status: 'sending'
    };
    
    addMessage(userMessage);
    clearError();
    
    try {
      // Send message to backend
      const response = await apiClient.sendTextMessage(content);
      
      // Update user message status
      updateMessage(userMessage.id, { status: 'sent' });
      
      // Create assistant message from backend response
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response.answer || "I'm sorry, I couldn't process your message.",
        role: 'assistant',
        timestamp: new Date().toISOString(),
        status: 'sent'
      };
      
      addMessage(assistantMessage);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      updateMessage(userMessage.id, { status: 'error' });
      setError('Failed to send message. Please try again.');
    }
  },

  addMessage: (message: Message) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  updateMessage: (id: string, updates: Partial<Message>) => {
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, ...updates } : msg
      ),
    }));
  },

  clearMessages: () => {
    set({ messages: [] });
  },

  setSessionId: (sessionId: string) => {
    set({ sessionId });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },

  setVapiConnected: (connected: boolean) => {
    set({ vapiConnected: connected });
  },

  setVapiCallId: (callId: string | null) => {
    set({ vapiCallId: callId });
  },
})); 