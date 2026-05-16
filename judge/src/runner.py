import subprocess
import tempfile
import os
from datetime import datetime
from pathlib import Path
from typing import Annotated
from fastapi import Body, Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy import update
from sqlmodel import create_engine, Session, SQLModel, select
from src.models.submission import Submission
from src.models.problem import Problem
# from src.models.problem import Problem
# from src.models.user import User
# from src.models.test_case import TestCase
# from src.schemas.submission import SubmissionCreate, SubmissionResponse
# from src.models.submission import Submission
# from src.database import SessionDep, create_db_and_tables
# from src.core.security import verify_access_token, get_current_user

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter()

@router.post("/runner", status_code=201)
def judge_submission(session: SessionDep, submission_id: int):
      # Check if the submission exists
      submission = session.exec(select(Submission).where(Submission.id == submission_id)).first()
      if not submission:
          raise HTTPException(status_code=404, detail="Submission not found")

      # Check if the problem exists
      problem_id = submission.problem_id
      problem = session.exec(select(Problem).where(Problem.id == problem_id)).first()
      if not problem:
          raise HTTPException(status_code=404, detail="Problem not found")
      result = session.exec(
          update(Submission).values(status="playing")
      )

      session.commit()
      # compile the code
      with tempfile.TemporaryDirectory() as temp_dir:
         temp_path = Path(temp_dir)
         source_file = temp_path / "main.cpp"
         exe_file = temp_path / "main"
         # write given source code to file
         source_code = submission.source_code
         source_file.write_text(source_code)
         # compile
         compile_result = subprocess.run(
             ["g++", str(source_file), "-o", str(exe_file)],
             capture_output=True,
           text=True
         )
        # todo : return responsesubmission with compile error
         if compile_result.returncode != 0:
             raise HTTPException(status_code=400, detail=f"Compilation failed: {compile_result.stderr}")
         return compile_result.returncode

#         # get test cases for the problem
#         test_cases = session.exec(select(TestCase).where(TestCase.problem_id == submissionCreate.problem_id)).all()

#         # run the executable with each test case and compare output
#         for test_case in test_cases:
#             # run the executable with the test case input
#             run_result = subprocess.run(
#                 [str(exe_file)],
#                 input=test_case.input_data,
#                 capture_output=True,
#                 text=True,
#                 # todo: add time limit and memory limit for the problem
#                 timeout=5  # set a timeout for execution
#             )

#             # check for runtime errors
#             if run_result.returncode != 0:
#                 raise HTTPException(status_code=400, detail=f"Runtime error: {run_result.stderr}")

#             # todo: measure execution time and include it in the response
#             # todo: handle time limit exceeded case and memory limit exceeded case
#             # todo : use checker_code and handle exceptions instead of manually checking returncode
#             # todo : set test_case number for test_case

#             # compare output with expected output
#             if run_result.stdout.strip() != test_case.expected_output.strip():
#                     return SubmissionResponse(
#                         problem_id=submissionCreate.problem_id,
#                         status=f"Wrong Answer on test: {test_case.id}",
#                         execution_time=None, 
#                         submitted_at=datetime.now() #
#                    )
#     return SubmissionResponse(
#         problem_id=submissionCreate.problem_id,
#         status="Accepted",
#         execution_time=None, 
#         submitted_at=datetime.now()
#     )


            
