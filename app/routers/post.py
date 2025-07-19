from typing import List, Optional
from fastapi import status, Response, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/",
            status_code=status.HTTP_200_OK,
            response_model=List[schemas.PostOut],
            )
def get_posts(db: Session = Depends(get_db),
              current_user=Depends(oauth2.get_current_user),
              limit: int = 100, offset: int = 0, search: Optional[str] = ""
              ):
    response = db. \
        query(models.Post, func.count(models.Vote.post_id).label("votes")). \
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True). \
        group_by(models.Post.id). \
        filter(models.Post.title.icontains(search).__or__(models.Post.content.icontains(search))). \
        order_by(models.Post.created_at.desc()). \
        limit(limit). \
        offset(offset). \
        all()

    return response


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=schemas.Post
             )
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user=Depends(oauth2.get_current_user)
                ):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/latest",
            status_code=status.HTTP_200_OK,
            response_model=schemas.Post
            )
def get_latest_post(db: Session = Depends(get_db)):
    """Get latest post"""
    lastest_post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()

    if lastest_post is None:
        return {"response": f"There is no post yet."}

    return lastest_post


@router.get("/{post_id}",
            status_code=status.HTTP_200_OK,
            response_model=schemas.PostOut
            )
def get_post_by_id(post_id: int, db: Session = Depends(get_db),
                   current_user=Depends(oauth2.get_current_user)
                   ):
    response = db. \
        query(models.Post, func.count(models.Vote.post_id).label("votes")). \
        join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True). \
        group_by(models.Post.id). \
        filter(models.Post.id == post_id). \
        first()

    if response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {post_id} does not found.")
    post = response[0]
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of the post.")

    return response


@router.delete("/{post_id}",
               status_code=status.HTTP_204_NO_CONTENT
               )
def delete_post(post_id: int, db: Session = Depends(get_db),
                current_user=Depends(oauth2.get_current_user)
                ):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    first_matched = post_query.first()

    if first_matched is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {post_id} does not found.")

    if first_matched.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of the post.")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{post_id}",
            status_code=status.HTTP_201_CREATED,
            response_model=schemas.Post
            )
def update_post(post_id: int, post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user=Depends(oauth2.get_current_user)
                ):
    db_query = db.query(models.Post).filter(models.Post.id == post_id)

    if db_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {post_id} does not found.")

    if db_query.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not the owner of the post.")

    db_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return db_query.first()
