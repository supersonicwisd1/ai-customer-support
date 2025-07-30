'use client';

import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

interface WidgetChatInputProps {
  className?: string;
  placeholder?: string;
  onSend: (content: string) => Promise<void>;
  disabled?: boolean;
}

export default function WidgetChatInput({ 
  className = '', 
  placeholder = 'Type your message...', 
  onSend, 
  disabled = false 
}: WidgetChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || disabled) return;

    const trimmedMessage = message.trim();
    setMessage('');
    
    try {
      await onSend(trimmedMessage);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 80)}px`;
    }
  }, [message]);

  return (
    <form onSubmit={handleSubmit} className={`flex items-end gap-2 ${className}`}>
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full resize-none border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          rows={1}
          style={{ minHeight: '40px', maxHeight: '80px' }}
        />
      </div>
      <button
        type="submit"
        disabled={!message.trim() || disabled}
        className="flex-shrink-0 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
      >
        <Send size={16} />
      </button>
    </form>
  );
} 