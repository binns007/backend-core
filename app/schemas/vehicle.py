from pydantic import BaseModel
from typing import Optional


class VehicleCreate(BaseModel):
    name: str
    first_service_time: Optional[str] = None
    service_kms: Optional[int] = None
    total_price: float


class VehicleResponse(BaseModel):
    id: int
    dealership_id: int
    name: str
    first_service_time: Optional[str]
    service_kms: Optional[int]
    total_price: float

    class Config:
        orm_mode = True
