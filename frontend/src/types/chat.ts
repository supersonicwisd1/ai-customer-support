export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  status: 'sending' | 'sent' | 'error';
  sources?: Source[];
  confidence?: number;
  processingTime?: number;
  audioUrl?: string;
}

export interface Source {
  title: string;
  url: string;
  content: string;
  relevanceScore: number;
  source: string;
}

export interface ChatResponse {
  message: string;
  sources: string[];
  confidence: number;
  session_id: string;
  timestamp: string;
  processing_time: number;
  tokens_used?: number;
}

export interface VoiceInfo {
  available: boolean;
  supported_voices: string[];
  features: {
    speech_to_text: boolean;
    text_to_speech: boolean;
    real_time: boolean;
  };
}

export interface VoiceChatResponse {
  transcription: string;
  response: string;
  session_id: string;
  confidence: number;
  sources: string[];
  audio_url: string;
}

export interface ChatSettings {
  voice: string;
  responseLength: 'short' | 'medium' | 'long';
  includeSources: boolean;
  autoPlayAudio: boolean;
} 