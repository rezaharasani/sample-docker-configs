from typing import List
from fastapi import status, Response, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/",
            status_code=status.HTTP_200_OK,
            response_model=List[schemas.PostOut]
            )
def get_posts(db: Session = Depends(get_db)):
    """Get all posts"""
    posts = db.query(models.Post).order_by(models.Post.id).all()
    return posts


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.PostOut
             )
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Create a new post"""
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/latest",
            status_code=status.HTTP_200_OK,
            response_model=schemas.PostOut
            )
def get_latest_post(db: Session = Depends(get_db)):
    """Get latest post"""
    lastest_post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()

    if lastest_post is None:
        return {"response": f"There is no post yet."}
    return lastest_post


@router.get("/{post_id}",
            response_model=schemas.PostOut
            )
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    """Get post by id"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {post_id} does not found.")
    return post


@router.delete("/{post_id}",
               status_code=status.HTTP_204_NO_CONTENT
               )
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete post by id"""
    post_query = db.query(models.Post).filter(models.Post.id == post_id)

    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {post_id} does not found.")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{post_id}",
            status_code=status.HTTP_201_CREATED,
            response_model=schemas.PostOut
            )
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Update post"""
    post_query = db.query(models.Post).filter(models.Post.id == post_id)

    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {post_id} does not found.")

    db.query(models.Post).filter(models.Post.id == post_id).update(post.model_dump(),
                                                                   synchronize_session=False)
    db.commit()
    return post_query.first()
