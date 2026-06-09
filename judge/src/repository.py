from sqlalchemy import update
from sqlmodel import Session, select
from src.models.submission import Submission, SubmissionStatus
from src.models.problem import Problem
from src.verdict import verdict_value

class JudgeSubmissionError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

def load_submission_for_judging(session: Session, submission_id: int):
    # Check if the submission exists
    submission = session.exec(
        select(Submission).where(Submission.id == submission_id)
    ).first()
    if not submission:
        raise JudgeSubmissionError(status_code=404, detail="Submission not found")

    # Check if the submission verdict is "in queue"
    if submission.verdict != SubmissionStatus.IN_QUEUE:
        message = (
            f"Submission {submission_id} verdict is not in queue: "
            f"{verdict_value(submission.verdict)}"
        )
        print(message, flush=True)
        return None, None

    # Check if the problem exists
    problem = session.exec(
        select(Problem).where(Problem.id == submission.problem_id)
    ).first()
    if not problem:
        raise JudgeSubmissionError(status_code=404, detail="Problem not found")
    return submission, problem

def finish_submission(
    session: Session,
    submission_id: int,
    verdict: SubmissionStatus,
    message: str,
    execution_time: float | None = None,
    execution_memory: float | None = None,
):
    session.exec(
        update(Submission)
        .values(
            verdict=verdict,
            execution_time=execution_time,
            execution_memory=execution_memory,
        )
        .where(
            (Submission.id == submission_id)
            & (Submission.verdict == SubmissionStatus.IN_QUEUE)
        )
    )
    session.commit()
    return message
