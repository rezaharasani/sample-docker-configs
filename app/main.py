from typing import List
from sqlalchemy.orm import Session
from .routers import user, post
from fastapi import FastAPI, status, Response, HTTPException, Depends
from . import models, schemas, utils
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    """display root page"""
    return {"message": "welcome to my api"}
