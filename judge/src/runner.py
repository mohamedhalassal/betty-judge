import subprocess
import tempfile
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Annotated
from fastapi import Body, Depends, FastAPI, HTTPException, APIRouter
from sqlalchemy import update
from sqlmodel import create_engine, Session, SQLModel, select
from src.models.submission import Submission
from src.models.problem import Problem
from src.models.test_case import TestCase
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

def validation(session: Session,submission_id: int):
      # Check if the submission exists
      submission = session.exec(select(Submission).where(Submission.id == submission_id)).first()
      if not submission:
          raise HTTPException(status_code=404, detail="Submission not found")
      
      # Check if the submission status is "in queue"
      if submission.status != "in queue":
          raise HTTPException(status_code=400, detail="Submission status is not in queue")
      
      # Check if the problem exists
      problem = session.exec(select(Problem).where(Problem.id == submission.problem_id)).first()
      if not problem:
          raise HTTPException(status_code=404, detail="Problem not found")
      return submission,problem
          
@router.post("/runner", status_code=201)
def judge_submission(session: SessionDep, submission_id: int):
      submission , problem = validation(session,submission_id)
  
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
        # todo : what should i return ?


         # compilation error
         if compile_result.returncode != 0:
            result = session.exec(
            update(Submission).values(status="compile error").
            where((Submission.id == submission_id) & (Submission.status == "in queue")))
            session.commit()
            return f"Compile error: {compile_result.stderr}"
     
        # get test cases for the problem
         test_cases = session.exec(select(TestCase).where(TestCase.problem_id == submission.problem_id)).all()
         execution_time = 0 
         memory_usage = 0 

        # run the executable with each test case and compare output
         for test_case in test_cases:
            # run the executable with the test case input
            try:
              process = subprocess.Popen(
                [str(exe_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
              stdout, stderr = process.communicate(
                input=test_case.input_data,
                timeout=problem.time_limit,
            )
            # time limit exceeded
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                session.exec(
                    update(Submission)
                    .values(status="time limit exceeded")
                    .where((Submission.id == submission_id) & (Submission.status == "in queue"))
                )
                session.commit()
                return f"Time Limit Exceeded on test: {test_case.id}"
            
            # check for runtime errors
            if process.returncode != 0:
                result = session.exec(
                    update(Submission).values(status="runtime error").
                    where((Submission.id == submission_id) & (Submission.status == "in queue")))
                session.commit()
                return f"Runtime Error on test: {test_case.id}, error: {stderr}"

            # measure execution time and memory usage
            pid, status, usage = os.wait4(process.pid, 0)
            cpu_time = usage.ru_utime + usage.ru_stime
            memory_kb = usage.ru_maxrss
            memory_usage = max(memory_usage, memory_kb)
            execution_time = max(execution_time, cpu_time)

            # check memory limit exceeded
            if(memory_usage > problem.memory_limit):
                session.exec(
                    update(Submission)
                    .values(status="memory limit exceeded",
                    execution_time=execution_time,execution_memory=memory_usage)
                    .where((Submission.id == submission_id) & (Submission.status == "in queue"))
                )
                session.commit()
                return f"Memory Limit Exceeded on test: {test_case.id}"
            
            # todo: measure execution time and include it in the response
            # todo: handle time limit exceeded case and memory limit exceeded case
            # todo : use checker_code and handle exceptions instead of manually checking returncode
            # todo : set test_case number for test_case

            # compare output with expected output
            if stdout.strip() != test_case.expected_output.strip():
                    result = session.exec(
                        update(Submission).values(status="wrong answer",
                        execution_time=execution_time,execution_memory=memory_usage).
                        where((Submission.id == submission_id) & (Submission.status == "in queue")))
                    session.commit()
                    return f"Wrong Answer on test: {test_case.id}"
        
         # if all test cases pass, update submission status to "accepted"
         finalresult = session.exec(
             update(Submission).values(status="accepted",
             execution_time=execution_time,execution_memory=memory_usage).
             where((Submission.id == submission_id) & (Submission.status == "in queue")))
         session.commit()
         return "Accepted"

                  



            
