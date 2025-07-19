'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Settings as SettingsIcon, Volume2, MessageSquare, Globe, Moon, Sun } from 'lucide-react';
import { useChatStore } from '@/store/chatStore';
import { apiClient } from '@/lib/api';
import { useTheme } from './ThemeProvider';

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function Settings({ isOpen, onClose }: SettingsProps) {
  const { settings, updateSettings, voiceAvailable } = useChatStore();
  const [availableVoices, setAvailableVoices] = useState<string[]>([]);
  const { theme, toggleTheme } = useTheme();

  // Load available voices when settings open
  useEffect(() => {
    if (isOpen && voiceAvailable) {
      apiClient.getVoiceInfo().then((voiceInfo) => {
        setAvailableVoices(voiceInfo.supported_voices || ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']);
      }).catch(() => {
        setAvailableVoices(['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']);
      });
    }
  }, [isOpen, voiceAvailable]);

  const handleVoiceChange = (voice: string) => {
    updateSettings({ voice });
  };

  const handleResponseLengthChange = (length: 'short' | 'medium' | 'long') => {
    updateSettings({ responseLength: length });
  };

  const handleIncludeSourcesChange = (include: boolean) => {
    updateSettings({ includeSources: include });
  };

  const handleAutoPlayChange = (autoPlay: boolean) => {
    updateSettings({ autoPlayAudio: autoPlay });
  };

  const toggleDarkMode = () => {
    toggleTheme();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={onClose}
          />

          {/* Settings Panel */}
          <motion.div
            initial={{ opacity: 0, x: '100%' }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-96 bg-white dark:bg-gray-800 shadow-2xl z-50 overflow-y-auto"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <SettingsIcon size={24} className="text-blue-500" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  Settings
                </h2>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Settings Content */}
            <div className="p-6 space-y-6">
              {/* Voice Settings */}
              {voiceAvailable && (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <Volume2 size={20} className="text-blue-500" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                      Voice Settings
                    </h3>
                  </div>

                  {/* Voice Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      AI Voice
                    </label>
                    <select
                      value={settings.voice}
                      onChange={(e) => handleVoiceChange(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {availableVoices.map((voice) => (
                        <option key={voice} value={voice}>
                          {voice.charAt(0).toUpperCase() + voice.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Auto-play Audio */}
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Auto-play audio responses
                      </label>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Automatically play AI voice responses
                      </p>
                    </div>
                    <button
                      onClick={() => handleAutoPlayChange(!settings.autoPlayAudio)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        settings.autoPlayAudio ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          settings.autoPlayAudio ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>
                </div>
              )}

              {/* Response Settings */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <MessageSquare size={20} className="text-blue-500" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Response Settings
                  </h3>
                </div>

                {/* Response Length */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Response Length
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['short', 'medium', 'long'] as const).map((length) => (
                      <button
                        key={length}
                        onClick={() => handleResponseLengthChange(length)}
                        className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                          settings.responseLength === length
                            ? 'bg-blue-500 text-white border-blue-500'
                            : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
                        }`}
                      >
                        {length.charAt(0).toUpperCase() + length.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Include Sources */}
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Include sources
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Show source links for AI responses
                    </p>
                  </div>
                  <button
                    onClick={() => handleIncludeSourcesChange(!settings.includeSources)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      settings.includeSources ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        settings.includeSources ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>

              {/* Appearance */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Globe size={20} className="text-blue-500" />
                  <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
                    Appearance
                  </h3>
                </div>

                {/* Dark Mode Toggle */}
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Dark mode
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Switch between light and dark themes
                    </p>
                  </div>
                  <button
                    onClick={toggleDarkMode}
                    className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                    {theme === 'dark' ? 'Light' : 'Dark'}
                  </button>
                </div>
              </div>

              {/* About */}
              <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
                <div className="text-center">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                    Aven AI Assistant
                  </h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Powered by OpenAI • Built with Next.js
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    Version 1.0.0
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
} 