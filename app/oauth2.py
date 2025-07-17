from datetime import timedelta, datetime, UTC
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, oauth2
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from . import schemas, models, database
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()

    expire_time = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire_time})

    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=user_id)
        return token_data

    except JWTError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(database.get_db)
                     ):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    db_user = db.query(models.User).filter(models.User.id == token.id).first()
    return db_user
