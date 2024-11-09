from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models
from schemas import employee
from core.utils import hash

def create_employee(employee_data: employee.EmployeeCreate, db: Session, current_user: models.User):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create employees"
        )
    
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == employee_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify all branch_ids belong to the current dealership
    for branch_id in employee_data.branch_ids:
        branch = db.query(models.Branch).filter(
            models.Branch.id == branch_id,
            models.Branch.dealership_id == current_user.dealership_id
        ).first()
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Branch with id {branch_id} not found or doesn't belong to your dealership"
            )
    
    # Create employee user
    hashed_password = hash(employee_data.password)
    employee_dict = employee_data.model_dump(exclude={'branch_ids', 'password'})
    new_employee = models.User(
        **employee_dict,
        password=hashed_password,
        dealership_id=current_user.dealership_id
    )
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return new_employee

def get_employees(db: Session, current_user: models.User):
    return db.query(models.User).filter(
        models.User.dealership_id == current_user.dealership_id,
        models.User.role != models.RoleEnum.ADMIN
    ).all()

def update_employee(employee_id: int, employee_data: employee.EmployeeUpdate, db: Session, current_user: models.User):
    employee_query = db.query(models.User).filter(
        models.User.id == employee_id,
        models.User.dealership_id == current_user.dealership_id
    )
    employee_obj = employee_query.first()
    
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )
    

    
    employee_query.update(employee_data.model_dump(exclude_unset=True))
    db.commit()
    return employee_query.first()

def delete_employee(employee_id: int, db: Session, current_user: models.User):
    employee_query = db.query(models.User).filter(
        models.User.id == employee_id,
        models.User.dealership_id == current_user.dealership_id
    )
    employee = employee_query.first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )
    
    employee_query.delete()
    db.commit()
    return {"message": "Employee deleted successfully"}
