from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models
from schemas import employee
from core.utils import hash, verify
from core.otp import generate_otp, send_otp
import random, string
from datetime import datetime, timedelta

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


def activate_employee_account(activation_data: employee.EmployeeActivation, db: Session):
    # Get the employee by email
    employee = db.query(models.User).filter(models.User.email == activation_data.email).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Verify the current password
    if not verify(activation_data.current_password, employee.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )
    
    # Verify OTP
    otp_record = db.query(models.OTP).filter(
        models.OTP.email == activation_data.email,
        models.OTP.otp_code == activation_data.otp,
        models.OTP.verified == False,
        models.OTP.expiration_time > datetime.utcnow()
    ).first()
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    if not employee.phone_number:
        employee.phone_number = activation_data.phone_number
        
    employee.password = hash(activation_data.new_password)
    otp_record.verified = True
    
    db.commit()
    return {"message": "Account activated successfully"}



def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_employee_otp(email: str, db: Session):
    # Verify the employee exists
    employee = db.query(models.User).filter(models.User.email == email).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    

    # Generate new OTP
    otp_code = generate_otp()
    
    # Save OTP to database
    new_otp = models.OTP(
        email=email,
        otp_code=otp_code,
        expiration_time=datetime.utcnow() + timedelta(minutes=10),
        verified=False
    )
    
    # Delete any existing unverified OTPs for this email
    db.query(models.OTP).filter(
        models.OTP.email == email,
        models.OTP.verified == False
    ).delete()
    
    # Save new OTP
    db.add(new_otp)
    db.commit()
    
    # Send OTP via email
    try:
        send_otp(email, otp_code)
        return {"message": "OTP sent successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )
