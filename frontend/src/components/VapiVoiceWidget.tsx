'use client';

import { useState, useEffect, useRef } from 'react';
import { X, Phone } from 'lucide-react';
import { apiClient } from '@/lib/api';
import Vapi from '@vapi-ai/web';

interface VapiVoiceWidgetProps {
  className?: string;
}

export default function VapiVoiceWidget({ className = '' }: VapiVoiceWidgetProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [vapiConfig, setVapiConfig] = useState<any>(null);
  const [isCallActive, setIsCallActive] = useState(false);
  const vapiRef = useRef<Vapi | null>(null);

  useEffect(() => {
    initializeVapi();
    
    // Suppress the specific audio processor warning
    const originalConsoleError = console.error;
    console.error = (...args) => {
      const message = args[0];
      if (typeof message === 'string' && message.includes('Ignoring settings for browser- or platform-unsupported input processor(s): audio')) {
        // Suppress this specific warning
        console.warn('Audio processor warning suppressed - voice call will work normally');
        return;
      }
      // Log all other errors normally
      originalConsoleError.apply(console, args);
    };

    // Cleanup function
    return () => {
      console.error = originalConsoleError;
    };
  }, []);

  const initializeVapi = async () => {
    try {
      setIsLoading(true);
      setError(null);

      console.log('🔍 Initializing VAPI Web SDK...');
      console.log('🌐 Backend URL:', process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

      // Test backend connectivity
      try {
        console.log('🏥 Testing backend health...');
        const healthResponse = await apiClient.getBackendHealth();
        console.log('✅ Backend health check passed:', healthResponse);
      } catch (healthError: any) {
        console.error('❌ Backend health check failed:', healthError);
        throw new Error('Backend server is not available');
      }

      // Get VAPI configuration
      try {
        console.log('⚙️ Fetching VAPI configuration from backend...');
        const config = await apiClient.getVapiConfig();
        console.log('✅ VAPI config received from backend:', config);
        
        if (config.success && config.config) {
          setVapiConfig(config.config);
          console.log('✅ VAPI Web SDK ready with config:', {
            assistantId: config.config.assistant_id,
            apiKeyLength: config.config.api_key?.length || 0,
            hasConfig: !!config.config.config
          });
        } else {
          throw new Error('Invalid VAPI configuration from backend');
        }
      } catch (configError: any) {
        console.error('❌ VAPI config failed:', configError);
        throw new Error('Failed to get VAPI configuration from backend');
      }

    } catch (error: any) {
      console.error('❌ Initialization failed:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const startCall = async () => {
    if (!vapiConfig) {
      setError('VAPI configuration not available');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      console.log('📞 Starting voice call with VAPI Web SDK...');
      console.log('🔗 Using backend assistant:', {
        assistantId: vapiConfig.assistant_id,
        apiKeyPrefix: vapiConfig.api_key?.substring(0, 10) + '...',
        backendConnected: true
      });

      // Check microphone permissions first
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log('✅ Microphone permission granted');
        // Stop the test stream
        stream.getTracks().forEach(track => track.stop());
      } catch (permissionError) {
        console.error('❌ Microphone permission denied:', permissionError);
        setError('Microphone permission denied. Please allow microphone access and try again.');
        return;
      }

      // Initialize VAPI Web SDK with API key from backend
      console.log('🔧 Initializing VAPI instance with backend config...');
      vapiRef.current = new Vapi(vapiConfig.api_key);

      // Set up event listeners BEFORE starting the call
      vapiRef.current.on('call-start', () => {
        console.log('📞 Call started successfully with backend assistant');
      });

      vapiRef.current.on('call-end', () => {
        console.log('📞 Call ended normally');
        setIsCallActive(false);
        vapiRef.current = null;
      });

      vapiRef.current.on('error', (error: any) => {
        console.error('❌ Call error:', error);
        setError(`Voice call error: ${error.message || 'Unknown error'}`);
        setIsCallActive(false);
        vapiRef.current = null;
      });

      vapiRef.current.on('speech-start', () => {
        console.log('🎤 Speech started');
      });

      vapiRef.current.on('speech-end', () => {
        console.log('🎤 Speech ended');
      });

      vapiRef.current.on('message', (message: any) => {
        console.log('💬 Message from backend assistant:', message.content);
      });

      // Start the call with assistant ID from backend
      console.log('🚀 Starting call with backend assistant ID:', vapiConfig.assistant_id);
      await vapiRef.current.start(vapiConfig.assistant_id);
      
      setIsCallActive(true);
      console.log('✅ Voice call started successfully with backend connection');

    } catch (error: any) {
      console.error('❌ Voice call failed:', error);
      console.error('Error details:', {
        message: error.message,
        stack: error.stack,
        name: error.name
      });
      
      // More specific error messages
      let errorMessage = 'Voice call failed';
      if (error.message?.includes('Meeting ended')) {
        errorMessage = 'Voice call connection failed. Please check your microphone permissions and try again.';
      } else if (error.message?.includes('network')) {
        errorMessage = 'Network error. Please check your internet connection.';
      } else if (error.message?.includes('permission')) {
        errorMessage = 'Microphone permission denied. Please allow microphone access and try again.';
      } else if (error.message?.includes('assistant')) {
        errorMessage = 'Assistant configuration error. Please try again later.';
      } else {
        errorMessage = `Voice call failed: ${error.message}`;
      }
      
      setError(errorMessage);
      vapiRef.current = null;
    } finally {
      setIsLoading(false);
    }
  };

  const endCall = async () => {
    if (vapiRef.current) {
      try {
        await vapiRef.current.stop();
        console.log('📞 Call ended manually');
      } catch (error: any) {
        console.error('❌ Error ending call:', error);
      }
    }
    setIsCallActive(false);
    vapiRef.current = null;
  };

  const retryInitialization = () => {
    setError(null);
    initializeVapi();
  };

  return (
    <div className={`relative ${className}`}>
      {/* Voice Button */}
      <button
        onClick={isCallActive ? endCall : startCall}
        disabled={isLoading || !vapiConfig}
        className={`
          flex items-center justify-center w-12 h-12 rounded-full transition-all duration-200
          ${isCallActive 
            ? 'bg-red-500 hover:bg-red-600 text-white' 
            : 'bg-green-500 hover:bg-green-600 text-white'
          }
          ${isLoading || !vapiConfig ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          shadow-lg hover:shadow-xl
        `}
        title={isCallActive ? 'End voice call' : 'Start voice call'}
      >
        {isLoading ? (
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : isCallActive ? (
          <X size={20} />
        ) : (
          <Phone size={20} />
        )}
      </button>

      {/* Status Indicator */}
      {vapiConfig && !isLoading && (
        <div className="ml-3 flex items-center">
          <div className={`w-2 h-2 rounded-full mr-2 ${isCallActive ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`} />
          <span className={`text-xs ${isCallActive ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
            {isCallActive ? 'In Call' : 'Ready'}
          </span>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="absolute top-full left-0 mt-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg shadow-lg z-10 min-w-64">
          <div className="text-red-700 dark:text-red-300 text-sm mb-2">{error}</div>
          <button
            onClick={retryInitialization}
            className="text-red-500 hover:text-red-700 text-xs"
          >
            Retry
          </button>
        </div>
      )}
    </div>
  );
}