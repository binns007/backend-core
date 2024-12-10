from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime
import schemas.chat as chat_schemas
import models
from services import employee as employee_service
from core import oauth2
from services import chat_manager
from schemas import employee
from database import get_db
import database
import json
from services.chat_manager import RoleTypes 


role_mapping = {
    "SALES_EXECUTIVE": RoleTypes.SALES_EXECUTIVE,
    "CUSTOMER": RoleTypes.CUSTOMER
}


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.get("/session-by-form/{form_instance_id}", response_model=chat_schemas.ChatSessionResponse)
async def get_chat_session_by_form(
    form_instance_id: int,
    db: Session = Depends(get_db)
):
    """
    Get chat session ID associated with a form instance
    """
    chat_session = db.query(models.ChatSession).filter(
        models.ChatSession.form_instance_id == form_instance_id,
        models.ChatSession.status == "ACTIVE"
    ).first()
    
    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active chat session found for this form"
        )
    
    return chat_session

@router.websocket("/ws/{session_id}/{role}")
async def chat_websocket(
    websocket: WebSocket,
    session_id: int,
    role: str,
    token: Optional[str] = None
):
    """WebSocket endpoint for chat functionality"""
    db = next(get_db())  # Get a new database session
    try:
        # Validate session exists and is active
        chat_session = db.query(models.ChatSession).filter(
            models.ChatSession.id == session_id,
            models.ChatSession.status == "ACTIVE"
        ).first()
        
        if not chat_session:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.error(f"Chat session {session_id} not found or not active")
            return

        # Map frontend role names to internal roles (case-insensitive)
        role = role.upper()
        internal_role = role_mapping.get(role)
        if not internal_role:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.error(f"Invalid role: {role}")
            return

        # Validate user authentication for sales executive role
        if internal_role == RoleTypes.SALES_EXECUTIVE:
            if not token:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                logger.error("Sales executive connection attempted without token")
                return
                
            try:
                user = await oauth2.get_current_user_from_token(token, db)
                if not user or user.role != models.RoleEnum.SALES_EXECUTIVE or user.id != chat_session.employee_id:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    logger.error("Invalid token or unauthorized sales executive")
                    return
            except Exception as e:
                logger.error(f"Authentication error details: {str(e)}", exc_info=True)
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

        # For customer role, validate against form_instance_id
        if internal_role == RoleTypes.CUSTOMER:
            # The validation is implicit through the chat session lookup
            # If they have the correct session_id, they can connect
            pass

        # Accept WebSocket connection
        await websocket.accept()
        logger.info(f"Accepted WebSocket connection for {role} in session {session_id}")
        
        # Send connection acknowledgment
        await websocket.send_json({
            "type": "connection_established",
            "role": role,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Register connection with chat manager
        await chat_manager.chat_manager.connect(websocket, session_id, internal_role)

        # Fetch and send message history
        messages = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == session_id
        ).order_by(models.ChatMessage.created_at.asc()).all()

        if messages:
            history_message = {
                "type": "history",
                "messages": [{
                    "id": msg.id,
                    "content": msg.content,
                    "sender_type": msg.sender_type.upper(),
                    "sender_id": msg.sender_id,
                    "created_at": msg.created_at.isoformat()
                } for msg in messages]
            }
            await websocket.send_json(history_message)
            logger.debug(f"Sent message history to {role} in session {session_id}")
        
        while True:
            try:
                # Receive and validate message
                data = await websocket.receive_json()
                logger.debug(f"Received message from {role} in session {session_id}: {data}")
                
                # Validate message structure
                if not isinstance(data, dict):
                    raise ValueError("Message must be a JSON object")
                if "content" not in data:
                    raise ValueError("Message must contain 'content' field")
                if not isinstance(data["content"], str):
                    raise ValueError("Message content must be a string")
                if not data["content"].strip():
                    raise ValueError("Message content cannot be empty")

                # Create and save message
                message = models.ChatMessage(
                    session_id=session_id,
                    sender_type=internal_role,
                    sender_id=chat_session.employee_id if internal_role == RoleTypes.SALES_EXECUTIVE else None,
                    content=data["content"]
                )
                db.add(message)
                db.commit()
                db.refresh(message)

                # Format message for broadcast
                formatted_message = {
                    "type": "message",
                    "data": {
                        "id": message.id,
                        "content": message.content,
                        "sender_type": message.sender_type.upper(),
                        "sender_id": message.sender_id,
                        "created_at": message.created_at.isoformat()
                    }
                }

                # First send to the sender
                await websocket.send_json(formatted_message)
                logger.debug(f"Sent message confirmation to sender {role} in session {session_id}")

                # Then broadcast to other participants
                await chat_manager.chat_manager.broadcast_message(
                    session_id,
                    formatted_message,
                    internal_role
                )
                logger.debug(f"Broadcasted message from {role} in session {session_id}")

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {role} in session {session_id}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except ValueError as e:
                logger.error(f"Invalid message format from {role} in session {session_id}: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                raise

    except WebSocketDisconnect:
        await chat_manager.chat_manager.disconnect(session_id, internal_role, websocket)
        logger.info(f"{role} disconnected from session {session_id}")
    except Exception as e:
        logger.error(f"Unhandled websocket error: {str(e)}", exc_info=True)
        if not websocket.client_state.DISCONNECTED:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        db.close() 

@router.post("/sessions", response_model=chat_schemas.ChatSessionResponse)
async def create_chat_session(
    form_instance_id: int,
    customer_name: str = "Anonymous Customer",
    db: Session = Depends(get_db)
):
    """
    Create a new chat session for a form instance
    """
    # Check if an active session already exists for this form instance
    existing_session = db.query(models.ChatSession).filter(
        models.ChatSession.form_instance_id == form_instance_id,
        models.ChatSession.status == "ACTIVE"
    ).first()
    
    if existing_session:
        return existing_session

    # Find an available sales executive
    employee = db.query(models.User).filter(
        models.User.is_activated == True,
        models.User.role == models.RoleEnum.sales_executive
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No available sales executives to handle chat"
        )
    
    # Create new chat session
    new_session = models.ChatSession(
        form_instance_id=form_instance_id,
        customer_name=customer_name,
        employee_id=employee.id,
        status="ACTIVE",
        created_at=datetime.utcnow()
    )
    
    try:
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chat session: {str(e)}"
        )

@router.get("/sessions", response_model=List[chat_schemas.ChatSessionResponse])
async def get_chat_sessions(
    db: Session = Depends(get_db)
):
    """
    Get all chat sessions
    """
    return db.query(models.ChatSession).all()

@router.get("/sessions/{session_id}", response_model=chat_schemas.ChatSessionResponse)
async def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific chat session
    """
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session {session_id} not found"
        )
    return session

@router.put("/sessions/{session_id}/close")
async def close_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """
    Close a chat session
    """
    session = db.query(models.ChatSession).filter(
        models.ChatSession.id == session_id,
        models.ChatSession.employee_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or unauthorized"
        )
    
    session.status = "CLOSED"
    session.closed_at = datetime.utcnow()
    
    try:
        db.commit()
        return {"message": "Chat session closed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close chat session: {str(e)}"
        )