from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class BranchBase(BaseModel):
    name: str
    location: str

class BranchCreate(BranchBase):
    pass

class BranchResponse(BranchBase):
    id: int
    dealership_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None