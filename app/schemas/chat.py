from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatSessionBase(BaseModel):
    form_instance_id: int
    customer_name: str
    employee_id: int

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    id: int
    status: str
    created_at: datetime
    closed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    content: str
    sender_type: str
    sender_id: Optional[int]

class ChatMessageCreate(ChatMessageBase):
    session_id: int

class ChatMessageResponse(ChatMessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True