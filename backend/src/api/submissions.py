from typing import Annotated
from fastapi import Body, Depends, FastAPI, HTTPException, APIRouter
from sqlmodel import select
from src.models.submission import Submission
from src.models.problem import Problem
from src.schemas.submission import SubmissionCreate
from src.models.user import User
from src.database import SessionDep, create_db_and_tables
from src.core.security import verify_access_token, get_current_user
router = APIRouter()

@router.get("/submissions",dependencies=[Depends(verify_access_token)]) #pyright: ignore
def read_submissions(session: SessionDep):
    statement = select(Submission).order_by(Submission.id)#pyright:ignore
    submissions = session.exec(statement).all()
    return submissions

@router.post("/submissions", status_code=201,dependencies=[Depends(verify_access_token)]) #pyright: ignore
async def create_submission(submission: Annotated[SubmissionCreate, Body(embed=False)], session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]):
    if(not session.exec(select(Problem).where(Problem.id == submission.problem_id)).first()): #pyright: ignore
            raise HTTPException(status_code=404, detail="Problem not found")
    submission_db = Submission(
        code=submission.code,
        problem_id=submission.problem_id,
        user_id=current_user.id)  #pyright: ignore
    session.add(submission_db)  #pyright: ignore
    session.commit()  #pyright: ignore
    session.refresh(submission_db)  #pyright: ignore
    return submission_db

@router.get("/submissions/{submission_id}",dependencies=[Depends(verify_access_token)]) #pyright: ignore
def read_submission(submission_id: int, session: SessionDep): #pyright: ignore
    submission = session.exec(select(Submission).where(Submission.id == submission_id)).first()#pyright: ignore
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
