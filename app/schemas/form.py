from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
import models


class FilledByEnum(str, Enum):
    SALES_EXECUTIVE = "sales_executive"
    CUSTOMER = "customer"

class FieldTypeEnum(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    IMAGE = "image"
    DATE = "date"

class FormFieldCreate(BaseModel):
    name: str
    field_type: FieldTypeEnum
    is_required: bool = True
    filled_by: FilledByEnum
    order: int

class FormFieldResponse(FormFieldCreate):
    id: int

    class Config:
        orm_mode = True

class FormTemplateCreate(BaseModel):
    name: str
    

class FormTemplateResponse(BaseModel):
    id: int
    name: str
    fields: List[FormFieldResponse] = []

    class Config:
        orm_mode = True
