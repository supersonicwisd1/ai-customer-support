'use client';

import React from 'react';
import { Message as MessageType } from '@/types/chat';
import { CheckCircle, Clock, AlertCircle, Mic } from 'lucide-react';

interface MessageProps {
  message: MessageType;
}

export default function Message({ message }: MessageProps) {
  const getStatusIcon = () => {
    switch (message.status) {
      case 'sent':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'sending':
        return <Clock size={16} className="text-yellow-500" />;
      case 'error':
        return <AlertCircle size={16} className="text-red-500" />;
      default:
        return null;
    }
  };

  const getRoleIcon = () => {
    if (message.isVoiceMessage) {
      return <Mic size={14} className="text-blue-500" />;
    }
    return null;
  };

  const formatMessageContent = (content: string) => {
    // Split content into paragraphs
    const paragraphs = content.split('\n\n');
    
    return paragraphs.map((paragraph, index) => {
      // Handle numbered lists
      if (paragraph.match(/^\d+\.\s/)) {
        const listItems = paragraph.split('\n').filter(item => item.trim());
        return (
          <div key={index} className="mb-3">
            {listItems.map((item, itemIndex) => {
              // Extract the number and content
              const numberMatch = item.match(/^(\d+)\.\s/);
              const number = numberMatch ? numberMatch[1] : '';
              const content = item.replace(/^\d+\.\s/, '');
              
              // Format the content (handle bold text)
              const formattedContent = content
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 dark:text-blue-400 underline hover:text-blue-800">$1</a>');
              
              return (
                <div key={itemIndex} className="flex items-start gap-2 mb-2">
                  <span className="text-sm font-medium text-blue-600 dark:text-blue-400 min-w-[20px]">
                    {number}.
                  </span>
                  <div 
                    className="text-sm leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: formattedContent }}
                  />
                </div>
              );
            })}
          </div>
        );
      }
      
      // Handle regular paragraphs
      const formattedParagraph = paragraph
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-blue-600 dark:text-blue-400 underline hover:text-blue-800">$1</a>');
      
      return (
        <div key={index} className="mb-3">
          <div 
            className="text-sm leading-relaxed"
            dangerouslySetInnerHTML={{ __html: formattedParagraph }}
          />
        </div>
      );
    });
  };

  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg message-bubble ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
        }`}
      >
        <div className="flex items-start gap-2">
          {getRoleIcon()}
          <div className="flex-1 min-w-0 chat-message">
            {formatMessageContent(message.content)}
          </div>
          {getStatusIcon()}
        </div>
        <div className="text-xs opacity-70 mt-2 flex items-center justify-between">
          <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
          {message.role === 'assistant' && (
            <span className="text-xs opacity-50">Aven AI</span>
          )}
        </div>
      </div>
    </div>
  );
} 