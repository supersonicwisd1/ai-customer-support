'use client';

import { useState } from 'react';
import { Message as MessageType } from '@/types/chat';
import { motion } from 'framer-motion';
import { 
  ExternalLink, 
  Play, 
  Pause, 
  Volume2, 
  ChevronDown, 
  ChevronUp,
  Clock,
  TrendingUp
} from 'lucide-react';

interface MessageProps {
  message: MessageType;
}

export default function Message({ message }: MessageProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);

  const isUser = message.role === 'user';
  const hasAudio = message.audioUrl;
  const hasSources = message.sources && message.sources.length > 0;

  const handleAudioPlay = async () => {
    if (!hasAudio) return;

    try {
      if (!audioElement) {
        const audio = new Audio(message.audioUrl);
        audio.onended = () => setIsPlaying(false);
        setAudioElement(audio);
      }

      if (isPlaying) {
        audioElement?.pause();
        setIsPlaying(false);
      } else {
        await audioElement?.play();
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Audio playback error:', error);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-500';
    if (confidence >= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
        }`}
      >
        {/* Message Content */}
        <div className="mb-2">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>

        {/* Message Metadata */}
        <div className="flex items-center justify-between text-xs opacity-70 mt-2">
          <span>{formatTime(message.timestamp)}</span>
          
          <div className="flex items-center gap-2">
            {message.processingTime && (
              <div className="flex items-center gap-1">
                <Clock size={12} />
                <span>{message.processingTime.toFixed(1)}s</span>
              </div>
            )}
            
            {message.confidence && (
              <div className="flex items-center gap-1">
                <TrendingUp size={12} />
                <span className={getConfidenceColor(message.confidence)}>
                  {(message.confidence * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Audio Playback (Assistant messages only) */}
        {!isUser && hasAudio && (
          <div className="mt-3 flex items-center gap-2">
            <button
              onClick={handleAudioPlay}
              className="flex items-center gap-2 px-3 py-1.5 bg-blue-500 text-white rounded-full text-sm hover:bg-blue-600 transition-colors"
            >
              {isPlaying ? <Pause size={14} /> : <Play size={14} />}
              <span>{isPlaying ? 'Pause' : 'Play'} Response</span>
            </button>
            <Volume2 size={16} className="text-gray-500" />
          </div>
        )}

        {/* Sources (Assistant messages only) */}
        {!isUser && hasSources && (
          <div className="mt-3">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-2 text-sm text-blue-500 hover:text-blue-600 transition-colors"
            >
              {showSources ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              <span>Sources ({message.sources!.length})</span>
            </button>
            
            {showSources && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-2 space-y-2"
              >
                {message.sources!.map((source, index) => (
                  <div
                    key={index}
                    className="p-2 bg-gray-50 dark:bg-gray-700 rounded-lg text-xs"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium">{source.title}</span>
                      <span className="text-gray-500">
                        {(source.relevanceScore * 100).toFixed(0)}% relevant
                      </span>
                    </div>
                    <p className="text-gray-600 dark:text-gray-300 mb-2 line-clamp-2">
                      {source.content || source.url}
                    </p>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-blue-500 hover:text-blue-600 transition-colors"
                    >
                      <ExternalLink size={12} />
                      <span>View Source</span>
                    </a>
                  </div>
                ))}
              </motion.div>
            )}
          </div>
        )}

        {/* Status Indicator */}
        {message.status === 'sending' && (
          <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span>AI is thinking...</span>
          </div>
        )}

        {message.status === 'error' && (
          <div className="mt-2 text-xs text-red-500">
            ❌ Message failed to send
          </div>
        )}
      </div>
    </motion.div>
  );
} 