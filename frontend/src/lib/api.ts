import { ChatResponse, VoiceInfo, VoiceChatResponse } from '@/types/chat';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  // Text Chat
  async sendMessage(message: string, sessionId?: string): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/chat/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        include_sources: true,
      }),
    });

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Voice Chat
  async sendVoiceMessage(audioBlob: Blob, sessionId?: string): Promise<VoiceChatResponse> {
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'audio.wav');
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const response = await fetch(`${this.baseUrl}/api/voice/chat`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Voice chat request failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Text to Speech
  async synthesizeSpeech(text: string, voice: string = 'alloy'): Promise<Blob> {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('voice', voice);

    const response = await fetch(`${this.baseUrl}/api/voice/synthesize`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Speech synthesis failed: ${response.statusText}`);
    }

    return response.blob();
  }

  // Get Voice Info
  async getVoiceInfo(): Promise<VoiceInfo> {
    const response = await fetch(`${this.baseUrl}/api/voice/voices`);
    
    if (!response.ok) {
      throw new Error(`Failed to get voice info: ${response.statusText}`);
    }

    return response.json();
  }

  // Health Check
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }

  // Voice Health Check
  async voiceHealthCheck(): Promise<{ status: string; available: boolean }> {
    const response = await fetch(`${this.baseUrl}/api/voice/health`);
    
    if (!response.ok) {
      throw new Error(`Voice health check failed: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiClient = new ApiClient(); 