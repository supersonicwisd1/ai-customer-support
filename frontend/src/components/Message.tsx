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

  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
        }`}
      >
        <div className="flex items-center gap-2">
          {getRoleIcon()}
          <span className="text-sm">{message.content}</span>
          {getStatusIcon()}
        </div>
        <div className="text-xs opacity-70 mt-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
} 