import time
from fastapi import FastAPI, status, Response, HTTPException, Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from sqlalchemy.orm import Session
from app import models
from app.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

"""
Define logger code for printing logging output as a formatted and pretty style. 
"""
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(funcName)15s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres",
                                password="password123", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        logger.info(f"{__name__}: Database connection was established!. Let's go :)")
        break

    except Exception as error:
        logger.error(f"{__name__}: Connecting to database failed.", error)
        time.sleep(2)


@app.get("/")
def root():
    return {"message": "welcome to my api"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"message": "welcome to sqlalchemy"}


@app.get("/posts", status_code=status.HTTP_200_OK)
def get_posts():
    cursor.execute("""SELECT * FROM posts ORDER BY id ASC;""")
    posts = cursor.fetchall()
    return {"response": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute(
        """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *;""",
        (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"response": new_post}


@app.get("/posts/latest", status_code=status.HTTP_200_OK)
def get_latest_post():
    cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC LIMIT 1;""")
    latest_post = cursor.fetchone()

    if latest_post is None:
        return {"response": f"There is no post yet."}
    return {"response": latest_post}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s;""", (str(post_id),))
    post = cursor.fetchone()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not found.")
    return {"response": post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", (str(post_id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}", status_code=status.HTTP_201_CREATED)
def update_post(post_id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s 
                WHERE id = %s RETURNING *;""",
        (post.title, post.content, post.published, str(post_id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} does not found.")
    return {"response": updated_post}
