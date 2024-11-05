from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from services import auth
from schemas import user
import database
import models
from core import utils
from core import otp
from datetime import datetime, timedelta

router = APIRouter(
    tags=['Auth']
)

@router.post("/register-admin", status_code=status.HTTP_201_CREATED, response_model=user.AdminUserOut)
def register_admin_user(user: user.AdminUserCreate, db: Session) -> models.User:
    # Check if the email has been verified
    otp_entry = db.query(models.OTP).filter(models.OTP.email == user.email, models.OTP.verified == True).first()
    if not otp_entry:
        raise ValueError("Email has not been verified")

    # Check if the user already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise ValueError("Email already registered")
    
    # Validate passwords match
    if user.password != user.confirm_password:
        raise ValueError("Passwords do not match")

    hashed_password = utils.hash(user.password)
    
    # Create new user
    new_user = models.User(
        first_name=user.first_name,
        last_name = user.last_name,
        email=user.email,
        password_hash=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(email: str, db: Session = Depends(database.get_db)):
    # existing_user = db.query(models.User).filter(models.User.email == email).first()
    # if existing_user:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    otp_code = otp.generate_otp()
    expiration_time = datetime.utcnow() + timedelta(minutes=10)  # OTP valid for 10 minutes
    otp_entry = models.OTP(email=email, otp_code=otp_code, expiration_time=expiration_time)
    db.add(otp_entry)
    db.commit()
    
    otp.send_otp(email, otp_code)
    
    return {"msg": "OTP sent to your email."}

@router.post("/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp(email: str, otp_code: str, db: Session = Depends(database.get_db)):
    otp_entry = db.query(models.OTP).filter(models.OTP.email == email, models.OTP.otp_code == otp_code).first()
    if not otp_entry or otp_entry.expiration_time < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    otp_entry.verified = True  # Mark the OTP as verified
    db.commit()
    
    return {"msg": "Email verified successfully."}



@router.post('/login', response_model=user.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    try:
        token = auth.authenticate_user(user_credentials, db)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
