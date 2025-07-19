from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import database, models, schemas, oauth2

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def post_vote(vote: schemas.Vote, db: Session = Depends(database.get_db),
              current_user=Depends(oauth2.get_current_user)
              ):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {vote.post_id} does not exist.")

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    matched_vote = vote_query.first()

    # add new entered vote into the votes table
    if vote.dir == 1:
        if matched_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"User {current_user.id} has already voted on post {vote.post_id}.")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": f"Post {vote.post_id} was successfully added."}

    # delete the given vote from the votes table
    elif vote.dir == 0:
        if not matched_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist.")

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": f"Post {vote.post_id} was successfully deleted."}

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="'dir' variable is not valid. Valid dir input is either 1 or 0.")
