'use client';

import dynamic from 'next/dynamic';

const ChatContainer = dynamic(() => import('@/components/ChatContainer'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-screen bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">Loading Aven AI Assistant...</p>
      </div>
    </div>
  ),
});

export default function Home() {
  return <ChatContainer />;
} 