import { create } from 'zustand';
import { Message, ChatSettings } from '@/types/chat';
import { apiClient } from '@/lib/api';

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  sessionId: string | null;
  settings: ChatSettings;
  voiceAvailable: boolean;
  error: string | null;
  
  // Actions
  sendMessage: (content: string) => Promise<void>;
  sendVoiceMessage: (audioBlob: Blob) => Promise<void>;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  clearMessages: () => void;
  setSessionId: (sessionId: string) => void;
  updateSettings: (settings: Partial<ChatSettings>) => void;
  setVoiceAvailable: (available: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  sessionId: null,
  settings: {
    voice: 'alloy',
    responseLength: 'medium',
    includeSources: true,
    autoPlayAudio: false,
  },
  voiceAvailable: false,
  error: null,

  sendMessage: async (content: string) => {
    const { sessionId, addMessage, updateMessage, setError } = get();
    
    // Create user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date(),
      status: 'sent',
    };
    
    addMessage(userMessage);
    
    // Create assistant message placeholder
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      status: 'sending',
    };
    
    addMessage(assistantMessage);
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiClient.sendMessage(content, sessionId || undefined);
      
      updateMessage(assistantMessage.id, {
        content: response.message,
        status: 'sent',
        confidence: response.confidence,
        processingTime: response.processing_time,
        sources: response.sources.map((url, index) => ({
          title: `Source ${index + 1}`,
          url,
          content: '',
          relevanceScore: 0.8,
          source: 'search',
        })),
      });
      
      // Set session ID if not already set
      if (!sessionId && response.session_id) {
        get().setSessionId(response.session_id);
      }
      
    } catch (error) {
      updateMessage(assistantMessage.id, {
        content: 'Sorry, I encountered an error. Please try again.',
        status: 'error',
      });
      setError(error instanceof Error ? error.message : 'Unknown error occurred');
    } finally {
      set({ isLoading: false });
    }
  },

  sendVoiceMessage: async (audioBlob: Blob) => {
    const { sessionId, addMessage, updateMessage, setError } = get();
    
    // Create user message with audio indicator
    const userMessage: Message = {
      id: Date.now().toString(),
      content: '🎤 Voice message',
      role: 'user',
      timestamp: new Date(),
      status: 'sent',
    };
    
    addMessage(userMessage);
    
    // Create assistant message placeholder
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      status: 'sending',
    };
    
    addMessage(assistantMessage);
    set({ isLoading: true, error: null });
    
    try {
      const response = await apiClient.sendVoiceMessage(audioBlob, sessionId || undefined);
      
      updateMessage(userMessage.id, {
        content: `🎤 "${response.transcription}"`,
      });
      
      updateMessage(assistantMessage.id, {
        content: response.response,
        status: 'sent',
        confidence: response.confidence,
        audioUrl: response.audio_url,
        sources: response.sources.map((url, index) => ({
          title: `Source ${index + 1}`,
          url,
          content: '',
          relevanceScore: 0.8,
          source: 'search',
        })),
      });
      
      // Set session ID if not already set
      if (!sessionId && response.session_id) {
        get().setSessionId(response.session_id);
      }
      
    } catch (error) {
      updateMessage(assistantMessage.id, {
        content: 'Sorry, I encountered an error processing your voice message. Please try again.',
        status: 'error',
      });
      setError(error instanceof Error ? error.message : 'Voice processing failed');
    } finally {
      set({ isLoading: false });
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

  updateSettings: (settings: Partial<ChatSettings>) => {
    set((state) => ({
      settings: { ...state.settings, ...settings },
    }));
  },

  setVoiceAvailable: (available: boolean) => {
    set({ voiceAvailable: available });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },
})); 