from fastapi import WebSocket
from typing import Dict, Set
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

class RoleTypes:
    SALES_EXECUTIVE = "sales_executive"  # Matches RoleEnum.SALES_EXECUTIVE.value
    CUSTOMER = "customer"

class ChatManager:
    def __init__(self):
        self.active_sessions: Dict[int, Dict[str, Set[WebSocket]]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: int, role: str):
        """Connect a client to a chat session"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {}
        if role not in self.active_sessions[session_id]:
            self.active_sessions[session_id][role] = set()
        self.active_sessions[session_id][role].add(websocket)
        logger.info(f"Connected {role} to session {session_id}")
        
    async def disconnect(self, session_id: int, role: str, websocket: WebSocket):
        """Disconnect a client from a chat session"""
        try:
            if session_id in self.active_sessions and role in self.active_sessions[session_id]:
                self.active_sessions[session_id][role].remove(websocket)
                if not self.active_sessions[session_id][role]:
                    del self.active_sessions[session_id][role]
                if not self.active_sessions[session_id]:
                    del self.active_sessions[session_id]
                logger.info(f"Disconnected {role} from session {session_id}")
        except KeyError:
            logger.warning(f"Attempted to disconnect non-existent session/role: {session_id}/{role}")
        except Exception as e:
            logger.error(f"Error during disconnect: {str(e)}")
                
    async def broadcast_message(self, session_id: int, message: dict, sender_role: str):
        """
        Broadcast message to all connected clients in the session except sender.
        """
        if session_id in self.active_sessions:
            for role, websockets in self.active_sessions[session_id].items():
                if role != sender_role:  # Don't send back to sender
                    disconnected_sockets = set()
                    for websocket in websockets:
                        try:
                            logger.debug(f"Broadcasting message in session {session_id} from {sender_role} to {role}")
                            await websocket.send_json(message)
                        except Exception as e:
                            logger.error(f"Error broadcasting message to {role} in session {session_id}: {str(e)}")
                            disconnected_sockets.add(websocket)
                    
                    # Clean up disconnected sockets
                    for ws in disconnected_sockets:
                        await self.disconnect(session_id, role, ws)

chat_manager = ChatManager()