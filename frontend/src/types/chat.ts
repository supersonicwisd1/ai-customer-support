export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string | Date;
  status: 'sending' | 'sent' | 'error';
  isVoiceMessage?: boolean;
}

export interface VapiConfig {
  api_key: string;
  assistant_id: string;
  config: {
    button: {
      color: string;
      text: string;
      icon: string;
    };
    widget: {
      position: string;
      theme: string;
    };
  };
}

export interface VapiCall {
  call_id: string;
  status: string;
  session_id: string;
  assistant_id: string;
}

export interface VapiHealth {
  status: string;
  vapi_connected: boolean;
  assistant_id?: string;
  error?: string;
  timestamp: string;
} 