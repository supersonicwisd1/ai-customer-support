'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

export default function TestPage() {
  const [backendStatus, setBackendStatus] = useState<string>('Testing...');
  const [vapiStatus, setVapiStatus] = useState<string>('Testing...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    testConnections();
  }, []);

  const testConnections = async () => {
    try {
      // Test basic backend connectivity
      console.log('Testing backend connectivity...');
      const health = await apiClient.getBackendHealth();
      console.log('Backend health:', health);
      setBackendStatus('✅ Backend Connected');

      // Test VAPI config
      console.log('Testing VAPI config...');
      const vapiConfig = await apiClient.getVapiConfig();
      console.log('VAPI config:', vapiConfig);
      setVapiStatus('✅ VAPI Config Available');

    } catch (error: any) {
      console.error('Connection test failed:', error);
      setError(error.message);
      setBackendStatus('❌ Connection Failed');
      setVapiStatus('❌ VAPI Config Failed');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Connection Test
        </h1>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="font-medium">Backend Status:</span>
            <span className={backendStatus.includes('✅') ? 'text-green-600' : 'text-red-600'}>
              {backendStatus}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="font-medium">VAPI Status:</span>
            <span className={vapiStatus.includes('✅') ? 'text-green-600' : 'text-red-600'}>
              {vapiStatus}
            </span>
          </div>
          
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <h3 className="font-semibold text-red-800 dark:text-red-200 mb-2">Error:</h3>
              <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
            </div>
          )}
          
          <button
            onClick={testConnections}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Retry Tests
          </button>
        </div>
        
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">Debug Info:</h3>
          <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
            <li>• API Base URL: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}</li>
            <li>• Frontend URL: {typeof window !== 'undefined' ? window.location.origin : 'Unknown'}</li>
            <li>• Check browser console for detailed logs</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 