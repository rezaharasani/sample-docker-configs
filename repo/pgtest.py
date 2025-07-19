import time
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

"""
Define logger code for printing logging output as a formatted and pretty style. 
"""
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(asctime)s - %(levelname)s - %(funcName)15s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)


def make_connection(message: str = "Database connection was established!. Let's go :)"):
    """
    Trying to connect to the PostgreSQL database, repeatedly.
    """
    while True:
        try:
            # create connection with fastapi database
            conn = psycopg2.connect(host="172.16.112.149", database="metabasedb", user="metabase", port="5433",
                                    password="password123", cursor_factory=RealDictCursor)

            logger.info(f"{__name__}: {message}")
            cursor = conn.cursor()
            return conn, cursor

        except Exception as error:
            logger.error(f"{__name__}: Connecting to database failed.", error)
            time.sleep(2)


def display_recodes(conn, cursor):
    """
    Retrieving records from the database, post table.
    """
    cursor.execute("""SELECT * FROM posts ORDER BY id ASC;""")
    get_posts = cursor.fetchall()

    # Getting records from the post table, and then print them in output terminal.
    for i, post in enumerate(get_posts):
        post_id = post['id']
        title = post['title']
        content = post['content']
        published = post['published']
        created_at = post['created_at']

        record = f"{i + 1}: {post_id} | {title} | {content} | {published} | {created_at}"
        logger.info(record)

    logger.info(f"{__name__}: {cursor.rowcount} records are fetched!")


def delete_post(conn, cursor, post_id: int) -> bool:
    """
    Delete a record from the post table.
    """
    if is_deleted(conn, cursor, post_id):
        logger.error(f"{__name__}: Requested post with id {post_id} was not found.")
        exit(1)

    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", (str(post_id),))
    deleted_post = cursor.fetchone()
    logger.info(f"{__name__}: Deleted post: {deleted_post}")
    conn.commit()
    logger.info(f"{__name__}: Deletion operation was commited into database.")


def is_deleted(conn, cursor, post_id: int):
    """
    Check if a record is deleted from the post table.
    """
    cursor.execute("""SELECT * FROM posts WHERE id = %s;""", (str(post_id),))
    if cursor.rowcount == 0:
        logger.info(f"{__name__}: Post id {str(post_id)} was successfully deleted.")
        return True
    else:
        logger.error(f"{__name__}: An error occurred while deleting post {str(post_id)}.")
        return False


if __name__ == '__main__':
    conn, cursor = make_connection(
        message="Retrieving table data connection was established! Keep going :)")

    cursor.execute("""SELECT * FROM users ORDER BY id ASC;""")
    print(cursor.fetchall())

    # display_recodes(conn, cursor)

    # conn, cursor = make_connection(
    #   message="Deleting connection was established! Keep going :)")
    # post_id: int = 12
    # delete_post(conn, cursor, post_id)
    #
    # conn, cursor = make_connection(
    #   message="Checking of deletion connection was established! Keep going :)")
    # is_deleted(conn, cursor, post_id)
