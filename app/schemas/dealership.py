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
    
    
class DealershipCreate(BaseModel):
    name: str
    address: str
    contact_number: str 
    contact_email: EmailStr
    num_employees: int
    roles: List[RoleEnum]  # List of selected roles for the dealership