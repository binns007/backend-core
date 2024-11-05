from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    DEALER = "DEALER"
    SALES_EXECUTIVE = "SALES_EXECUTIVE"
    FINANCE = "FINANCE"
    RTO = "RTO"
    CUSTOMER = "CUSTOMER"
    
class AdminUserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    role: RoleEnum

    @classmethod
    def validate_role(cls, value):
        return value.upper()

    class Config:
        use_enum_values = True

class AdminUserOut(BaseModel):
    id: int
    first_name: str 
    last_name: str  # Assuming last_name is optional
    email: str
    role: RoleEnum

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int