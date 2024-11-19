from datetime import datetime, date
from pydantic import BaseModel, EmailStr,validator
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
    last_name: str
    email: str
    role: str

    @validator("role", pre=True)
    def convert_role(cls, v):
        return v.upper() if isinstance(v, str) else v
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int