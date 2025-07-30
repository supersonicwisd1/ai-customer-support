const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE = API_BASE.replace('http', 'ws');

// Log API configuration for debugging
if (typeof window !== 'undefined') {
  console.log('API Configuration:', {
    API_BASE,
    WS_BASE,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
  });
}

export class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  // Text Chat API
  async sendTextMessage(message: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`);
    }
    return response.json();
  }

  // VAPI Configuration
  async getVapiConfig(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/vapi/config`);
    if (!response.ok) {
      throw new Error(`Failed to get VAPI config: ${response.statusText}`);
    }
    return response.json();
  }

  // VAPI Health Check
  async getVapiHealth(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/vapi/health`);
    if (!response.ok) {
      throw new Error(`Failed to get VAPI health: ${response.statusText}`);
    }
    return response.json();
  }

  // VAPI Call Management
  async createVapiCall(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/vapi/calls`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id: sessionId }),
    });
    if (!response.ok) {
      throw new Error(`Failed to create VAPI call: ${response.statusText}`);
    }
    return response.json();
  }

  async getVapiCallStatus(callId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/vapi/calls/${callId}`);
    if (!response.ok) {
      throw new Error(`Failed to get VAPI call status: ${response.statusText}`);
    }
    return response.json();
  }

  async endVapiCall(callId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/vapi/calls/${callId}/end`, {
      method: 'PUT',
    });
    if (!response.ok) {
      throw new Error(`Failed to end VAPI call: ${response.statusText}`);
    }
    return response.json();
  }

  // Backend Health Check
  async getBackendHealth(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Backend health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  // WebSocket URL for VAPI (if needed)
  getWebSocketUrl(sessionId: string): string {
    return `ws://localhost:8000/ws/vapi/${sessionId}`;
  }
}

export const apiClient = new ApiClient(); 