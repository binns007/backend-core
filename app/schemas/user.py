from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Optional, List

class AdminUserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    role_id: int

class AdminUserOut(BaseModel):
    user_id: int
    first_name: str 
    last_name: str  # Assuming last_name is optional
    email: str
    role_name: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int