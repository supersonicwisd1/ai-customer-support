'use client';

import dynamic from 'next/dynamic';

const QuickChatWidget = dynamic(() => import('./QuickChatWidget'), {
  loading: () => <div>Loading chat widget...</div>,
});

export default function QuickChatWrapper() {
  return <QuickChatWidget />;
} 