from typing import Annotated
from fastapi import Body, Depends, FastAPI, HTTPException, APIRouter, Query
from sqlmodel import select
from src.models.submission import Submission, SubmissionStatus
from src.models.problem import Problem
from src.schemas.submission import SubmissionCreate, SubmissionResponse
from src.models.user import User
from src.database import SessionDep, create_db_and_tables
from src.core.security import verify_access_token, get_current_user

router = APIRouter()


@router.get("/submissions", response_model=list[SubmissionResponse])
def read_all_submissions(
    session: SessionDep,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    problem_id: Annotated[int | None, Query()] = None,
    username: Annotated[str | None, Query()] = None,
    verdict: Annotated[SubmissionStatus | None, Query()] = None,
):
    statement = select(Submission)

    if problem_id is not None:
        statement = statement.where(Submission.problem_id == problem_id)
    if username is not None:
        statement = statement.where(User.username == username).join(User, Submission.user_id == User.id)
    if verdict is not None:
        statement = statement.where(Submission.verdict == verdict)

    offset = (page - 1) * size
    statement = statement.order_by(Submission.id.desc()).offset(offset).limit(size)
    submissions = session.exec(statement).all()

    return submissions


@router.get(
    "/my-submissions",
    response_model=list[SubmissionResponse],
    dependencies=[Depends(verify_access_token)],
)  # pyright: ignore
def read_submissions(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    verdict: Annotated[SubmissionStatus | None, Query()] = None,
):  # pyright: ignore
    statement = select(Submission).where(
        Submission.user_id == current_user.id
    )  # pyright: ignore
    if verdict is not None:
        statement = statement.where(Submission.verdict == verdict)
    statement = statement.order_by(Submission.id.desc())  # pyright:ignore
    offset = (page - 1) * size
    statement = statement.offset(offset).limit(size)
    submissions = session.exec(statement).all()
    return submissions


@router.post(
    "/submit", status_code=201, dependencies=[Depends(verify_access_token)]
)  # pyright: ignore
async def create_submission(
    submission: Annotated[SubmissionCreate, Body(embed=False)],
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not session.exec(
        select(Problem).where(Problem.id == submission.problem_id)
    ).first():  # pyright: ignore
        raise HTTPException(status_code=404, detail="Problem not found")
    submission_db = Submission(
        source_code=submission.source_code,
        problem_id=submission.problem_id,
        user_id=current_user.id,
    )  # pyright: ignore
    session.add(submission_db)  # pyright: ignore
    session.commit()  # pyright: ignore
    session.refresh(submission_db)  # pyright: ignore
    return submission_db


@router.get(
    "/my-submissions/{submission_id}",
    response_model=SubmissionResponse,
    dependencies=[Depends(verify_access_token)],
)  # pyright: ignore
def read_submission(
    submission_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):  # pyright: ignore
    submission = session.exec(
        select(Submission).where(
            Submission.id == submission_id, Submission.user_id == current_user.id
        )
    ).first()  # pyright: ignore
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
