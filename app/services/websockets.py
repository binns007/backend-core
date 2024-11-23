import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List

class NotificationManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        try:
            await websocket.accept()
            if user_id not in self.active_connections:
                self.active_connections[user_id] = []
            self.active_connections[user_id].append(websocket)
        except Exception as e:
            print(f"Error connecting websocket: {str(e)}")
            await websocket.close(code=1011)

    def disconnect(self, websocket: WebSocket, user_id: int):
        try:
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        except Exception as e:
            print(f"Error disconnecting websocket: {str(e)}")

    async def broadcast_to_user(self, user_id: int, message: dict):
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)
            
            # Clean up any disconnected websockets
            for connection in disconnected:
                self.disconnect(connection, user_id)

notification_manager = NotificationManager()