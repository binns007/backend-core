from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum


class RoleEnum(str, Enum):
    admin = "admin"
    dealer = "dealer"
    sales_executive = "sales_executive"
    finance = "finance"
    rto = "rto"
    customer = "customer"
    
    
class DealershipCreate(BaseModel):
    name: str
    address: str
    contact_number: str 
    contact_email: EmailStr
    num_employees: int
    num_branches: int
    roles: List[RoleEnum]  # List of selected roles for the dealership