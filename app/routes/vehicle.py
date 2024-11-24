from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List,Dict
from schemas import vehicle
import database
import models
import logging
logging.basicConfig(level=logging.DEBUG)


router = APIRouter(
    prefix="/vehicle-data",
    tags=["Vehicle data"]
)


@router.post("/vehicles/", response_model=vehicle.VehicleResponse, status_code=201)
def create_vehicle(vehicle: vehicle.VehicleCreate, db: Session = Depends(database.get_db)):
    # Validate that the dealership exists (optional, if relevant)
    dealership = db.query(models.Dealership).filter_by(id=vehicle.dealership_id).first()
    if not dealership:
        raise HTTPException(status_code=404, detail="Dealership not found")

    # Create the new vehicle record
    new_vehicle = models.Vehicle(
        dealership_id=vehicle.dealership_id,
        name=vehicle.name,
        first_service_time=vehicle.first_service_time,
        service_kms=vehicle.service_kms,
        total_price=vehicle.total_price,
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle