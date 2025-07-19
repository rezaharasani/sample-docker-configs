from typing import List
from fastapi import status, Response, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/",
            status_code=status.HTTP_200_OK,
            response_model=List[schemas.UserOut]
            )
def get_users(db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user)
              ):
    """Get all users from database"""
    users = db.query(models.User).order_by(models.User.created_at).all()
    return users


@router.get("/{user_id}",
            status_code=status.HTTP_200_OK,
            response_model=schemas.UserOut
            )
def get_user_by_id(user_id: int, db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    """Get user by id"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id {user_id} does not found.")
    return user


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.UserOut
             )
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)
                ):
    """Create new user into database"""
    print(" ************ Creating new user")
    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
