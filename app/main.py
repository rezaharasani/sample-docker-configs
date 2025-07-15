from fastapi import FastAPI, status, Response, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def root():
    """display root page"""
    return {"message": "welcome to my api"}


@app.get("/posts", status_code=status.HTTP_200_OK)
def get_posts(db: Session = Depends(get_db)):
    """Get all posts"""
    posts = db.query(models.Post).all()
    return {"response": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Create a new post"""
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"response": new_post}


@app.get("/posts/latest", status_code=status.HTTP_200_OK)
def get_latest_post(db: Session = Depends(get_db)):
    """Get latest post"""
    lastest_post = db.query(models.Post).order_by(models.Post.created_at.desc()).first()

    if lastest_post is None:
        return {"response": f"There is no post yet."}
    return {"response": lastest_post}


@app.get("/posts/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get post by id"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not found.")
    return {"response": post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete post by id"""
    post_query = db.query(models.Post).filter(models.Post.id == post_id)

    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not found.")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}", status_code=status.HTTP_201_CREATED)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    """Update post"""
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not found.")

    db.query(models.Post).filter(models.Post.id == post_id).update(post.model_dump(), synchronize_session=False)
    db.commit()
    return {"response": post_query.first()}
