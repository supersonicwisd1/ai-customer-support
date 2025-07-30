'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

export default function Home() {
  const [backendStatus, setBackendStatus] = useState<string>('Checking...');

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const health = await apiClient.getBackendHealth();
        setBackendStatus('✅ Backend Connected');
        console.log('Backend health:', health);
      } catch (error) {
        setBackendStatus('❌ Backend Not Available');
        console.error('Backend connection failed:', error);
      }
    };

    checkBackend();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
            Aven AI Support System
          </h1>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
              Welcome to Aven's AI-Powered Customer Support
            </h2>
            
            <div className="space-y-4 text-left">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Backend Status:</span>
                <span className={`text-sm ${backendStatus.includes('✅') ? 'text-green-600' : 'text-red-600'}`}>
                  {backendStatus}
                </span>
              </div>
              
              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                  🎯 Features Available:
                </h3>
                <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                  <li>• AI-powered customer support with knowledge base</li>
                  <li>• Voice and text chat capabilities</li>
                  <li>• Real-time conversation with VAPI integration</li>
                  <li>• Comprehensive Aven service information</li>
                </ul>
              </div>
              
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                <h3 className="font-semibold text-green-900 dark:text-green-100 mb-2">
                  💡 How to Use:
                </h3>
                <ul className="text-sm text-green-800 dark:text-green-200 space-y-1">
                  <li>• Look for the chat widget in the bottom-right corner</li>
                  <li>• Click to open the AI assistant</li>
                  <li>• Type messages or use voice chat</li>
                  <li>• Get instant help with Aven services</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 