import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get('session_id');

    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID is required' },
        { status: 400 }
      );
    }

    // For development, use localhost:8000
    // In production, this would come from environment variables
    const baseUrl = process.env.NODE_ENV === 'production' 
      ? 'wss://your-production-domain.com'
      : 'ws://localhost:8000';

    const websocketUrl = `${baseUrl}/ws/chat/${sessionId}`;

    return NextResponse.json({
      websocket_url: websocketUrl,
      session_id: sessionId
    });

  } catch (error) {
    console.error('Error generating WebSocket URL:', error);
    return NextResponse.json(
      { error: 'Failed to generate WebSocket URL' },
      { status: 500 }
    );
  }
} 