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
    phone_number: str = Field(..., pattern=r'^\+?\d{10,15}$')
 


class EmployeeOTPRequest(BaseModel):
    email: EmailStr

class RoleUpdate(BaseModel):
    role: RoleEnum
    reason: str  # Optional field to document why the role was changed

class RoleResponse(BaseModel):
    name: str
    description: str

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    BOTH = "both"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SingleNotification(BaseModel):
    message: str
    notification_type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    subject: Optional[str] = None

class BatchNotificationFilter(BaseModel):
    branch_ids: Optional[List[int]] = None
    roles: Optional[List[RoleEnum]] = None
    employee_ids: Optional[List[int]] = None

class BatchNotification(SingleNotification):
    filters: BatchNotificationFilter

class NotificationCreate(BaseModel):
    user_id: int
    message: str
    title: Optional[str] = None
    notification_type: str = "system"

class NotificationResponse(BaseModel):
    id: int
    message: str
    title: Optional[str]
    is_read: bool
    created_at: datetime
    notification_type: str
    
    class Config:
        from_attributes = True