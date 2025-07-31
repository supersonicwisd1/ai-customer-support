'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Bot } from 'lucide-react';
import { useChatStore } from '@/store/chatStore';
import Message from './Message';
import VapiVoiceWidget from './VapiVoiceWidget';

interface ChatInterfaceProps {
  className?: string;
}

export default function ChatInterface({ className = '' }: ChatInterfaceProps) {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, sendMessage } = useChatStore();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const trimmedMessage = message.trim();
    setMessage('');

    try {
      setIsLoading(true);
      await sendMessage(trimmedMessage);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Bot size={20} className="text-blue-200" />
            <span className="font-semibold text-lg">Aven AI Assistant</span>
          </div>
        </div>
        <VapiVoiceWidget />
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 py-12">
            <div className="bg-white dark:bg-gray-800 rounded-lg p-8 shadow-sm border border-gray-200 dark:border-gray-700">
              <MessageCircle size={48} className="mx-auto mb-4 opacity-50 text-blue-500" />
              <h3 className="font-semibold mb-3 text-gray-700 dark:text-gray-300">Welcome to Aven AI Assistant!</h3>
              <p className="text-sm mb-6 text-gray-600 dark:text-gray-400 leading-relaxed">
                I can help you with information about Aven's services, credit cards, and more. 
                Ask me anything about our products, policies, or how to get started.
              </p>
              <div className="text-xs space-y-3 text-gray-500 dark:text-gray-500">
                <div className="flex items-center justify-center gap-2">
                  <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                  <p>💬 Type a message below to chat</p>
                </div>
                <div className="flex items-center justify-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  <p>📞 Use the voice button for voice conversation</p>
                </div>
                <div className="flex items-center justify-center gap-2">
                  <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                  <p>🔍 Ask about our credit cards, HELOC, or policies</p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <form onSubmit={handleSendMessage} className="flex gap-3">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me about Aven's services..."
            className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!message.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2 font-medium"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span className="hidden sm:inline">Sending...</span>
              </>
            ) : (
              <>
                <Send size={16} />
                <span className="hidden sm:inline">Send</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
} 