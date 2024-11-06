from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
from schemas import dealership



def register_dealership_service(
     dealership_data: dealership.DealershipCreate, db: Session,current_user: models.User
):
   
    # Create a new Dealership instance
    dealership = models.Dealership(
        name=dealership_data.name,
        address=dealership_data.address,
        contact_number=dealership_data.contact_number,
        num_employees=dealership_data.num_employees,
        contact_email=dealership_data.contact_email,
        # Set the creator_id to the current admin user's id
        creator_id=current_user.id
    )
    
    # Add the dealership to the database
    db.add(dealership)
    db.commit()

    # Link the dealership with the current admin user
    current_user.dealership_id = dealership.id
    db.commit()

    # Return a success message
    return {"message": "Dealership registered successfully", "dealership_id": dealership.id}