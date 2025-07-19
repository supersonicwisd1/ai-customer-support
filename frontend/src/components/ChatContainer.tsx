'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useChatStore } from '@/store/chatStore';
import Message from './Message';
import ChatInput from './ChatInput';
import Settings from './Settings';
import ClientOnly from './ClientOnly';
import { Bot, MessageCircle, Settings as SettingsIcon, Trash2 } from 'lucide-react';

export default function ChatContainer() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const { 
    messages, 
    isLoading, 
    error, 
    clearMessages, 
    clearError,
    voiceAvailable,
    setVoiceAvailable 
  } = useChatStore();
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Check voice availability on mount
  useEffect(() => {
    const checkVoiceAvailability = async () => {
      try {
        const { apiClient } = await import('@/lib/api');
        const voiceInfo = await apiClient.voiceHealthCheck();
        setVoiceAvailable(voiceInfo.available);
      } catch (error) {
        console.warn('Voice service not available:', error);
        setVoiceAvailable(false);
      }
    };

    checkVoiceAvailability();
  }, [setVoiceAvailable]);

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear all messages?')) {
      clearMessages();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 bg-blue-500 text-white rounded-full">
            <Bot size={24} />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Aven AI Assistant
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {voiceAvailable ? 'Voice & Text Chat Available' : 'Text Chat Only'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleClearChat}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-red-500 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Clear chat history"
          >
            <Trash2 size={16} />
            <span>Clear</span>
          </button>
          
          <button
            onClick={() => setIsSettingsOpen(true)}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            title="Settings"
          >
            <SettingsIcon size={16} />
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center h-full text-center"
            >
              <div className="flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900/20 text-blue-500 rounded-full mb-4">
                <MessageCircle size={32} />
              </div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                Welcome to Aven AI Assistant
              </h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-md">
                Ask me anything about Aven&apos;s services, rates, features, or get help with your account. 
                I can also help you with voice chat!
              </p>
              
              {/* Quick Start Suggestions */}
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg">
                {[
                  "What are Aven's current rates?",
                  "Tell me about Aven's features",
                  "How do I apply for a credit card?",
                  "What's the latest news from Aven?"
                ].map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => useChatStore.getState().sendMessage(suggestion)}
                    className="p-3 text-left text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </motion.div>
          ) : (
            messages.map((message) => (
              <Message key={message.id} message={message} />
            ))
          )}
        </AnimatePresence>

        {/* Loading indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-3 text-gray-500 dark:text-gray-400"
          >
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span className="text-sm">AI is thinking...</span>
          </motion.div>
        )}

        {/* Error message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
          >
            <div className="flex-shrink-0 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xs">!</span>
            </div>
            <div className="flex-1">
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
            <button
              onClick={clearError}
              className="flex-shrink-0 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
            >
              ×
            </button>
          </motion.div>
        )}

        {/* Scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <ChatInput />

      {/* Settings Modal */}
      <ClientOnly>
        <Settings isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      </ClientOnly>
    </div>
  );
} 