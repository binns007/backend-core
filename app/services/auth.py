from sqlalchemy.orm import Session
import models
import schemas
import core
from schemas import user
from fastapi.security.oauth2 import OAuth2PasswordRequestForm



def register_admin_user(user: user.AdminUserCreate, db: Session):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise ValueError("Email already registered")
    
    otp_entry = db.query(models.OTP).filter(models.OTP.email == user.email, models.OTP.verified == True).first()
    if not otp_entry:
        raise ValueError("Email has not been verified")

    hashed_password = core.utils.hash(user.password)
    
    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def authenticate_user(user_credentials: OAuth2PasswordRequestForm, db: Session) -> tuple:
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    # Check if user exists and the password is correct
    if not user or not core.utils.verify(user_credentials.password, user.password):
        raise ValueError("Invalid credentials")

    # Check activation status for non-admin users
    if user.role != models.RoleEnum.admin and not user.is_activated:
        raise ValueError("Please activate your account before logging in. Check your email for activation instructions.")

    # Create an access token
    access_token = core.oauth2.create_access_token(data={"user_id": user.id})

    # Return both the token and the user's role
    return access_token, user.role
