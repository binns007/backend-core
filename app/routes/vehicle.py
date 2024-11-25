from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List,Dict
from schemas import vehicle
from core import oauth2
import database
import models
import logging
from services import vehicle as vehicle_service
logging.basicConfig(level=logging.DEBUG)


router = APIRouter(
    prefix="/vehicle-data",
    tags=["Vehicle data"]
)


@router.post("/vehicles/", response_model=vehicle.VehicleResponse, status_code=201)
def create_vehicle(vehicle: vehicle.VehicleCreate,
                    db: Session = Depends(database.get_db),
                    current_user: models.User = Depends(oauth2.get_current_user_authenticated)
):


    # Create the new vehicle record
    new_vehicle = models.Vehicle(
        dealership_id=current_user.dealership_id,
        name=vehicle.name,
        first_service_time=vehicle.first_service_time,
        service_kms=vehicle.service_kms,
        total_price=vehicle.total_price,
    )
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)

    return new_vehicle



@router.get("/vehicles", response_model=list[vehicle.VehicleResponse])
def get_vehicles(
    db: Session = Depends(database.get_db),
    current_user=Depends(oauth2.get_current_user),
):
    """
    Fetch all vehicles for the current user's dealership.
    """
    return vehicle_service.get_vehicles_for_dealership(db, current_user)