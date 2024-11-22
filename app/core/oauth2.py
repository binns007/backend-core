from jose import JWTError, jwt
from datetime import datetime, timedelta
import models
from schemas import user
import database
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config import settings
from typing import Union

oauth2_scheme_user = OAuth2PasswordBearer(tokenUrl="login",auto_error=False)


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy() 

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})  

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token_user(token: str, credentials_exception):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = user.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data



def get_current_user(token: str = Depends(oauth2_scheme_user), db: Session = Depends(database.get_db)):
    # If no token is provided and we're accessing a public endpoint, return None
    if not token:
        return None
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = verify_access_token_user(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    
    # Check activation status only for non-admin users
    if user and not user.is_activated and user.role != models.RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not activated. Please activate your account first."
        )

    return user



def get_current_user_authenticated(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user

def get_current_user_from_token(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = verify_access_token_user(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    # Check activation status only for non-admin users
    if user and not user.is_activated and user.role != models.RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not activated. Please activate your account first."
        )

    if not user:
        raise credentials_exception

    return user