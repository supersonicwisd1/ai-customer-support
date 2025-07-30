import asyncio
import json
import logging
from typing import Dict, Any, Optional, Set, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages that can be sent/received via WebSocket"""
    # Connection messages
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Chat messages
    TEXT_MESSAGE = "text_message"
    VOICE_MESSAGE = "voice_message"
    AI_RESPONSE = "ai_response"
    TYPING_INDICATOR = "typing_indicator"
    
    # Voice-specific messages
    VOICE_START = "voice_start"
    VOICE_END = "voice_end"
    VOICE_TRANSCRIPTION = "voice_transcription"
    VOICE_SYNTHESIS = "voice_synthesis"
    
    # Status messages
    STATUS = "status"
    ERROR = "error"
    WARNING = "warning"

class ConnectionState(Enum):
    """Connection states for WebSocket clients"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"

class WebSocketManager:
    """Manages WebSocket connections for unified text and voice chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_states: Dict[str, ConnectionState] = {}
        self.session_data: Dict[str, Dict[str, Any]] = {}
        self.typing_users: Dict[str, Set[str]] = {}  # session_id -> set of user_ids
        
        logger.info("WebSocket Manager initialized")
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: Optional[str] = None) -> bool:
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Store connection
            connection_id = f"{session_id}_{user_id or 'anonymous'}"
            self.active_connections[connection_id] = websocket
            self.connection_states[connection_id] = ConnectionState.CONNECTED
            
            # Initialize session data
            if session_id not in self.session_data:
                self.session_data[session_id] = {
                    "created_at": datetime.utcnow().isoformat(),
                    "connections": [],
                    "message_count": 0,
                    "last_activity": datetime.utcnow().isoformat()
                }
            
            self.session_data[session_id]["connections"].append(connection_id)
            self.session_data[session_id]["last_activity"] = datetime.utcnow().isoformat()
            
            # Send connection confirmation
            await self.send_message(
                websocket,
                MessageType.CONNECT,
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "connection_id": connection_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "Connected to unified chat WebSocket"
                }
            )
            
            logger.info(f"WebSocket connected: {connection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket: {e}")
            return False
    
    async def disconnect(self, session_id: str, user_id: Optional[str] = None) -> bool:
        """Disconnect a WebSocket connection"""
        try:
            connection_id = f"{session_id}_{user_id or 'anonymous'}"
            
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                
                # Update state
                self.connection_states[connection_id] = ConnectionState.DISCONNECTING
                
                # Send disconnect message
                await self.send_message(
                    websocket,
                    MessageType.DISCONNECT,
                    {
                        "session_id": session_id,
                        "user_id": user_id,
                        "connection_id": connection_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": "Disconnected from chat"
                    }
                )
                
                # Close connection
                await websocket.close()
                
                # Clean up
                del self.active_connections[connection_id]
                del self.connection_states[connection_id]
                
                # Update session data
                if session_id in self.session_data:
                    if connection_id in self.session_data[session_id]["connections"]:
                        self.session_data[session_id]["connections"].remove(connection_id)
                    
                    # Remove session if no more connections
                    if not self.session_data[session_id]["connections"]:
                        del self.session_data[session_id]
                
                logger.info(f"WebSocket disconnected: {connection_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to disconnect WebSocket: {e}")
            return False
    
    async def send_message(self, websocket: WebSocket, message_type: MessageType, data: Dict[str, Any]) -> bool:
        """Send a message to a specific WebSocket connection"""
        try:
            # Check if connection is still active
            connection_id = None
            for conn_id, ws in self.active_connections.items():
                if ws == websocket:
                    connection_id = conn_id
                    break
            
            if not connection_id or self.connection_states.get(connection_id) != ConnectionState.CONNECTED:
                logger.warning(f"Attempted to send message to inactive connection")
                return False
            
            message = {
                "type": message_type.value,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_text(json.dumps(message))
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            # Mark connection as disconnected if send fails and clean up
            if connection_id:
                self.connection_states[connection_id] = ConnectionState.DISCONNECTED
                # Remove from active connections to prevent further attempts
                if connection_id in self.active_connections:
                    del self.active_connections[connection_id]
                # Clean up from session data
                for session_id, session_data in self.session_data.items():
                    if connection_id in session_data.get("connections", []):
                        session_data["connections"].remove(connection_id)
            return False
    
    async def broadcast_to_session(self, session_id: str, message_type: MessageType, data: Dict[str, Any], exclude_user: Optional[str] = None) -> int:
        """Broadcast a message to all connections in a session"""
        try:
            sent_count = 0
            
            if session_id in self.session_data:
                # Create a copy of connections to avoid modification during iteration
                connections = list(self.session_data[session_id]["connections"])
                
                for connection_id in connections:
                    # Skip if this is the excluded user
                    if exclude_user and connection_id.endswith(f"_{exclude_user}"):
                        continue
                    
                    if connection_id in self.active_connections:
                        websocket = self.active_connections[connection_id]
                        if await self.send_message(websocket, message_type, data):
                            sent_count += 1
                        else:
                            # Remove failed connection from session data
                            if connection_id in self.session_data[session_id]["connections"]:
                                self.session_data[session_id]["connections"].remove(connection_id)
                            # Also remove from active connections if not already done
                            if connection_id in self.active_connections:
                                del self.active_connections[connection_id]
                            if connection_id in self.connection_states:
                                del self.connection_states[connection_id]
            
            logger.debug(f"Broadcasted to {sent_count} connections in session {session_id}")
            return sent_count
            
        except Exception as e:
            logger.error(f"Failed to broadcast message: {e}")
            return 0
    
    async def send_typing_indicator(self, session_id: str, user_id: str, is_typing: bool) -> bool:
        """Send typing indicator to session participants"""
        try:
            if is_typing:
                if session_id not in self.typing_users:
                    self.typing_users[session_id] = set()
                self.typing_users[session_id].add(user_id)
            else:
                if session_id in self.typing_users:
                    self.typing_users[session_id].discard(user_id)
                    if not self.typing_users[session_id]:
                        del self.typing_users[session_id]
            
            # Broadcast typing indicator
            await self.broadcast_to_session(
                session_id,
                MessageType.TYPING_INDICATOR,
                {
                    "user_id": user_id,
                    "is_typing": is_typing,
                    "typing_users": list(self.typing_users.get(session_id, set()))
                },
                exclude_user=user_id
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send typing indicator: {e}")
            return False
    
    async def send_ai_response_stream(self, session_id: str, response_stream: List[str], user_id: Optional[str] = None) -> bool:
        """Send AI response as a stream to session participants"""
        try:
            # Send typing indicator
            await self.send_typing_indicator(session_id, "ai_assistant", True)
            
            # Stream the response
            full_response = ""
            for chunk in response_stream:
                full_response += chunk
                
                await self.broadcast_to_session(
                    session_id,
                    MessageType.AI_RESPONSE,
                    {
                        "chunk": chunk,
                        "is_partial": True,
                        "full_response": full_response,
                        "user_id": user_id
                    },
                    exclude_user=user_id
                )
                
                # Small delay to simulate streaming
                await asyncio.sleep(0.05)
            
            # Send final response
            await self.broadcast_to_session(
                session_id,
                MessageType.AI_RESPONSE,
                {
                    "chunk": "",
                    "is_partial": False,
                    "full_response": full_response,
                    "user_id": user_id
                },
                exclude_user=user_id
            )
            
            # Stop typing indicator
            await self.send_typing_indicator(session_id, "ai_assistant", False)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send AI response stream: {e}")
            return False
    
    async def send_voice_transcription_stream(self, session_id: str, transcription_stream: List[Dict[str, Any]], user_id: Optional[str] = None) -> bool:
        """Send voice transcription as a stream"""
        try:
            for transcription_chunk in transcription_stream:
                await self.broadcast_to_session(
                    session_id,
                    MessageType.VOICE_TRANSCRIPTION,
                    {
                        "transcription": transcription_chunk,
                        "user_id": user_id
                    },
                    exclude_user=user_id
                )
                
                await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send voice transcription stream: {e}")
            return False
    
    async def send_voice_synthesis_stream(self, session_id: str, audio_stream: List[bytes], user_id: Optional[str] = None) -> bool:
        """Send voice synthesis as a stream"""
        try:
            for audio_chunk in audio_stream:
                await self.broadcast_to_session(
                    session_id,
                    MessageType.VOICE_SYNTHESIS,
                    {
                        "audio_chunk": audio_chunk.hex(),  # Convert bytes to hex for JSON
                        "user_id": user_id
                    },
                    exclude_user=user_id
                )
                
                await asyncio.sleep(0.05)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send voice synthesis stream: {e}")
            return False
    
    def get_connection_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about connections in a session"""
        try:
            if session_id not in self.session_data:
                return {"error": "Session not found"}
            
            session_info = self.session_data[session_id].copy()
            session_info["active_connections"] = len(session_info["connections"])
            session_info["typing_users"] = list(self.typing_users.get(session_id, set()))
            
            return session_info
            
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            return {"error": str(e)}
    
    def get_all_sessions(self) -> Dict[str, Any]:
        """Get information about all active sessions"""
        try:
            sessions_info = {}
            for session_id, session_data in self.session_data.items():
                sessions_info[session_id] = self.get_connection_info(session_id)
            
            return {
                "total_sessions": len(sessions_info),
                "total_connections": len(self.active_connections),
                "sessions": sessions_info
            }
            
        except Exception as e:
            logger.error(f"Failed to get all sessions: {e}")
            return {"error": str(e)}
    
    async def ping_connections(self) -> Dict[str, Any]:
        """Ping all connections to check health"""
        try:
            ping_results: Dict[str, int] = {"success": 0, "failed": 0}
            
            for connection_id, websocket in self.active_connections.items():
                try:
                    await self.send_message(
                        websocket,
                        MessageType.PING,
                        {"timestamp": datetime.utcnow().isoformat()}
                    )
                    ping_results["success"] += 1
                except Exception:
                    ping_results["failed"] += 1
                    # Mark for cleanup
                    self.connection_states[connection_id] = ConnectionState.DISCONNECTED
            
            logger.info(f"Ping results: {ping_results}")
            return ping_results
            
        except Exception as e:
            logger.error(f"Failed to ping connections: {e}")
            return {"error": str(e)}
    
    async def cleanup_dead_connections(self) -> int:
        """Clean up disconnected connections"""
        try:
            cleaned_count = 0
            
            for connection_id, state in list(self.connection_states.items()):
                if state == ConnectionState.DISCONNECTED:
                    # Remove from active connections
                    if connection_id in self.active_connections:
                        del self.active_connections[connection_id]
                    
                    # Remove from connection states
                    del self.connection_states[connection_id]
                    
                    # Remove from session data
                    for session_id in list(self.session_data.keys()):
                        if connection_id in self.session_data[session_id]["connections"]:
                            self.session_data[session_id]["connections"].remove(connection_id)
                            
                            # Remove empty sessions
                            if not self.session_data[session_id]["connections"]:
                                del self.session_data[session_id]
                    
                    cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} dead connections")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup dead connections: {e}")
            return 0
    
    def is_connected(self, session_id: str, user_id: Optional[str] = None) -> bool:
        """Check if a user is connected to a session"""
        connection_id = f"{session_id}_{user_id or 'anonymous'}"
        return connection_id in self.active_connections
    
    def get_connection_count(self, session_id: str) -> int:
        """Get the number of active connections in a session"""
        if session_id in self.session_data:
            return len(self.session_data[session_id]["connections"])
        return 0 