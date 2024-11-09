from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import RoleEnum

class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: RoleEnum
    branch_id: Optional[int] = None

class EmployeeCreate(EmployeeBase):
    password: str
    branch_ids: List[int]  # Allow assigning to multiple branches

class EmployeeResponse(EmployeeBase):
    id: int
    dealership_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None
    branch_id: Optional[int] = None
    password: Optional[str] = None

class EmployeeActivation(BaseModel):
    email: EmailStr
    current_password: str
    new_password: str
    otp: str
    phone_number: str = Field(..., pattern=r'^\+?\d{10,15}$')
 


class EmployeeOTPRequest(BaseModel):
    email: EmailStr