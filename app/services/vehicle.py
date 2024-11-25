from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models, schemas

def get_vehicles_for_dealership(db: Session, current_user: models.User):
    """
    Get vehicles for the dealership associated with the current user.
    """
    # Ensure the user is associated with a dealership
    if not current_user.dealership_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with any dealership."
        )
    
    # Query vehicles for the dealership
    vehicles = db.query(models.Vehicle).filter(
        models.Vehicle.dealership_id == current_user.dealership_id
    ).all()

    # Convert to schema response
    return [
        schemas.vehicle.VehicleResponse(
            id=vehicle .id,
            name=vehicle.name,
            first_service_time=vehicle.first_service_time,
            service_kms=vehicle.service_kms,
            total_price=vehicle.total_price
        )
        for vehicle in vehicles
    ]
