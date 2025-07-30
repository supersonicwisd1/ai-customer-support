'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, CornerRightDown } from 'lucide-react';
import ChatInterface from './ChatInterface';

interface Size {
  width: number;
  height: number;
}

const MIN_SIZE: Size = { width: 300, height: 200 };
const MAX_SIZE: Size = { width: 600, height: 800 };
const DEFAULT_SIZE: Size = { width: 320, height: 400 };

export default function QuickChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [size, setSize] = useState<Size>(DEFAULT_SIZE);
  const [isResizing, setIsResizing] = useState(false);
  const [resizeStart, setResizeStart] = useState<{ x: number; y: number; width: number; height: number } | null>(null);
  const widgetRef = useRef<HTMLDivElement>(null);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      width: size.width,
      height: size.height
    });
  };

  const handleResizeMove = (e: MouseEvent) => {
    if (!isResizing || !resizeStart) return;

    const deltaX = e.clientX - resizeStart.x;
    const deltaY = e.clientY - resizeStart.y;

    // For top-left resize handle, we need to invert the logic
    // Dragging down/right should increase size, up/left should decrease
    const newWidth = Math.max(MIN_SIZE.width, Math.min(MAX_SIZE.width, resizeStart.width - deltaX));
    const newHeight = Math.max(MIN_SIZE.height, Math.min(MAX_SIZE.height, resizeStart.height - deltaY));

    setSize({ width: newWidth, height: newHeight });
  };

  const handleResizeEnd = () => {
    setIsResizing(false);
    setResizeStart(null);
  };

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleResizeMove);
      document.addEventListener('mouseup', handleResizeEnd);
      document.body.style.cursor = 'nw-resize';
      document.body.style.userSelect = 'none';

      return () => {
        document.removeEventListener('mousemove', handleResizeMove);
        document.removeEventListener('mouseup', handleResizeEnd);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isResizing, resizeStart]);

  return (
    <>
      {/* Chat Toggle Button */}
      <motion.button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        title="Chat with AI Assistant"
      >
        <MessageCircle size={24} />
      </motion.button>

      {/* Chat Widget */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            ref={widgetRef}
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="fixed bottom-24 right-6 z-40 bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden"
            style={{
              width: size.width,
              height: size.height
            }}
          >
            {/* Chat Interface */}
            <div className="h-full">
              <ChatInterface className="h-full" />
            </div>

            {/* Resize Handle - Top Left */}
            <div
              className="absolute top-0 left-0 w-6 h-6 cursor-nw-resize flex items-center justify-center bg-gray-200 dark:bg-gray-600 rounded-br-lg opacity-50 hover:opacity-100 transition-opacity"
              onMouseDown={handleResizeStart}
              title="Drag to resize"
            >
              <CornerRightDown size={12} className="text-gray-600 dark:text-gray-400 rotate-180" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}