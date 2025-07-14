import time
from datetime import datetime

from fastapi import FastAPI, status, Response, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

from sqlalchemy.dialects.mysql import insert

app = FastAPI()

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


while True:
    try:
        # create connection with fastapi database
        conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres",
                                password="catdogq", cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        logger.info("Database connection was successful!")
        break

    except Exception as error:
        logger.error("Connecting to database failed.", error)
        time.sleep(2)

my_posts = [
    {
        "id": 1,
        "title": "Reading fiction books",
        "content": "New version of Harry Potter book, version 7",
        "published": True,
        "rating": 5,
    },
    {
        "id": 2,
        "title": "Favorite foods",
        "content": "I like pizza",
        "published": False,
        "rating": 3,
    }
]


def find_post(post_id: int):
    for post in my_posts:
        if post["id"] == post_id:
            return post
    return None


def find_index_post(post_id: int):
    for index, post in enumerate(my_posts):
        if post["id"] == post_id:
            return index
    return None


@app.get("/")
def root():
    return {"message": "welcome to my api"}


@app.get("/posts")
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


@app.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts) - 1]
    return {"response": post}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s;""", (str(post_id),))
    post = cursor.fetchone()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} was not found.")
    return {"response": post}


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s;""", (str(post_id),))

    # index = find_index_post(post_id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} was not found.")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}", status_code=status.HTTP_201_CREATED)
def update_post(post_id: int, post: Post):
    index = find_index_post(post_id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} was not found.")
    post_dict = post.dict()
    post_dict['id'] = post_id
    my_posts[index] = post_dict
    return {"response": post_dict}
