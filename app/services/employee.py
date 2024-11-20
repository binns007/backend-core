from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models
from schemas import employee
from schemas.employee import NotificationType
from core.utils import hash, verify
from core.otp import generate_otp, send_otp
import random, string
from datetime import datetime, timedelta
from typing import Dict, Any
from core.notifications import send_email, send_sms, NotificationError




async def notify_employee(
    employee_id: int,
    notification_data: employee.SingleNotification,
    db: Session,
    current_user: models.User
) -> Dict[str, Any]:
    """
    Send notification to a single employee
    
    Args:
        employee_id: ID of employee to notify
        notification_data: Notification content and settings
        db: Database session
        current_user: Currently authenticated user
    
    Returns:
        Dict containing success message or error details
    
    Raises:
        HTTPException: For permission, validation or notification errors
    """
    # Check permissions
    if current_user.role != models.RoleEnum.ADMIN and current_user.id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only send notifications to yourself unless you're an admin"
        )
    
    # Get employee
    employee = db.query(models.User).filter(
        models.User.id == employee_id,
        models.User.dealership_id == current_user.dealership_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )

    notification_sent = False
    errors = []

    try:
        if notification_data.notification_type in [NotificationType.EMAIL, NotificationType.BOTH]:
            if employee.email:
                await send_email(
                    to_email=employee.email,
                    subject=notification_data.subject or "New Notification",
                    message=notification_data.message,
                    priority=notification_data.priority
                )
                notification_sent = True
            else:
                errors.append("Email address not available")

        if notification_data.notification_type in [NotificationType.SMS, NotificationType.BOTH]:
            if employee.phone_number:
                await send_sms(
                    to_phone=employee.phone_number,
                    message=notification_data.message,
                    priority=notification_data.priority
                )
                notification_sent = True
            else:
                errors.append("Phone number not available")

        if not notification_sent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not send notification: {', '.join(errors)}"
            )

        return {"message": "Notification sent successfully"}

    except NotificationError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Notification delivery failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error while sending notification: {str(e)}"
        )

async def notify_batch_employees(
    notification_data: employee.BatchNotification,
    db: Session,
    current_user: models.User
) -> Dict[str, Any]:
    """
    Send notifications to multiple employees based on filters
    
    Args:
        notification_data: Batch notification settings and content
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        Dict containing success/failure counts and details
    
    Raises:
        HTTPException: For permission or validation errors
    """
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can send batch notifications"
        )

    # Build query based on filters
    query = db.query(models.User).filter(
        models.User.dealership_id == current_user.dealership_id
    )

    filters = notification_data.filters
    if filters.branch_ids:
        query = query.filter(models.User.branch_id.in_(filters.branch_ids))
    if filters.roles:
        query = query.filter(models.User.role.in_(filters.roles))
    if filters.employee_ids:
        query = query.filter(models.User.id.in_(filters.employee_ids))

    employees = query.all()
    if not employees:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No employees found matching the specified criteria"
        )

    results = {
        "total_employees": len(employees),
        "success_count": 0,
        "failure_count": 0,
        "failures": []
    }

    for employee in employees:
        try:
            if notification_data.notification_type in [NotificationType.EMAIL, NotificationType.BOTH]:
                if employee.email:
                    try:
                        await send_email(
                            to_email=employee.email,
                            subject=notification_data.subject or "New Notification",
                            message=notification_data.message,
                            priority=notification_data.priority
                        )
                        results["success_count"] += 1
                    except NotificationError as e:
                        results["failures"].append(f"Employee {employee.id} email failed: {str(e)}")
                        results["failure_count"] += 1
                else:
                    results["failures"].append(f"Employee {employee.id}: Email address not available")
                    results["failure_count"] += 1

            if notification_data.notification_type in [NotificationType.SMS, NotificationType.BOTH]:
                if employee.phone_number:
                    try:
                        await send_sms(
                            to_phone=employee.phone_number,
                            message=notification_data.message,
                            priority=notification_data.priority
                        )
                        results["success_count"] += 1
                    except NotificationError as e:
                        results["failures"].append(f"Employee {employee.id} SMS failed: {str(e)}")
                        results["failure_count"] += 1
                else:
                    results["failures"].append(f"Employee {employee.id}: Phone number not available")
                    results["failure_count"] += 1

        except Exception as e:
            results["failures"].append(f"Employee {employee.id}: Unexpected error: {str(e)}")
            results["failure_count"] += 1

    # Only include failures list if there were any failures
    if not results["failures"]:
        results.pop("failures")

    return results


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
        dealership_id=current_user.dealership_id,
        is_activated=False
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
    
    # Check if account is already activated
    if employee.is_activated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already activated"
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
    
    # Update employee information
    if not employee.phone_number:
        employee.phone_number = activation_data.phone_number
    
    employee.password = hash(activation_data.new_password)
    employee.is_activated = True  # Mark account as activated
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


def get_employee_by_id(employee_id: int, db: Session, current_user: models.User):
    """Get detailed information about a specific employee"""
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can view detailed employee information"
        )
    
    employee = db.query(models.User).filter(
        models.User.id == employee_id,
        models.User.dealership_id == current_user.dealership_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )
    
    return employee

def update_employee_role(
    employee_id: int,
    role_update: employee.RoleUpdate,
    db: Session,
    current_user: models.User
):
    """Update an employee's role"""
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update employee roles"
        )
    
    employee = db.query(models.User).filter(
        models.User.id == employee_id,
        models.User.dealership_id == current_user.dealership_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} not found"
        )
    
    # Update the role
    employee.role = role_update.role
    db.commit()
    db.refresh(employee)
    
    return employee

def get_available_roles(db: Session, current_user: models.User):
    """Get list of all available roles with descriptions"""
    roles_info = [
        employee.RoleResponse(
            name=models.RoleEnum.DEALER.value,
            description="Can manage overall dealership operations"
        ),
        employee.RoleResponse(
            name=models.RoleEnum.SALES_EXECUTIVE.value,
            description="Handles sales and customer interactions"
        ),
        employee.RoleResponse(
            name=models.RoleEnum.FINANCE.value,
            description="Manages financial aspects and transactions"
        ),
        employee.RoleResponse(
            name=models.RoleEnum.RTO.value,
            description="Handles vehicle registration and documentation"
        )
    ]
    return roles_info


