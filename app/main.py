from fastapi import FastAPI
from . import models
from .database import engine
from .routers import user, post, auth, vote

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PANDA",
    description="Python and FastAPI Project",
    version="v0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    deprecated=False
)

app.include_router(user.router)
app.include_router(post.router)
app.include_router(vote.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "welcome to my api"}
