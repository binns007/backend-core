from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect, 
    Depends, Query
)
from core import oauth2
from database import get_db
from sqlalchemy.orm import Session
from services.websockets import notification_manager

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/notifications")
async def websocket_notifications(
    websocket: WebSocket, 
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        # Authenticate user
        current_user = await oauth2.get_current_user_from_token(token, db)
        
        if not current_user:
            await websocket.close(code=4003, reason="Authentication failed")
            return
            
        # Connect to notification manager
        await notification_manager.connect(websocket, current_user.id)
        
        try:
            # Keep connection alive and handle messages
            while True:
                data = await websocket.receive_text()
                # You can handle incoming messages here if needed
                
        except WebSocketDisconnect:
            # Handle disconnection
            notification_manager.disconnect(websocket, current_user.id)
            
    except Exception as e:
        await websocket.close(code=1008, reason=str(e))


router.add_websocket_route(
    "/notifications", 
    websocket_notifications
)