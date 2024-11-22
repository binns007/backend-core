from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect, 
    Depends, Query
)
from core import oauth2
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/ws", tags=["WebSocket"])

async def websocket_notifications(
    websocket: WebSocket, 
    token: str = Query(..., description="Authentication token"),
    db: Session = Depends(get_db)
):
    try:
        # Authenticate user
        current_user = await oauth2.get_current_user_from_token(token, db)
        
        # Accept the WebSocket connection
        await websocket.accept()
        
        # Main WebSocket handling logic
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    
    except WebSocketDisconnect:
        # Handle disconnection
        pass
    except Exception as e:
        # Handle other exceptions
        await websocket.close(code=1008)


router.add_websocket_route(
    "/notifications", 
    websocket_notifications
)