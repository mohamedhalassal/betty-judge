import subprocess
import tempfile
import resource
import math
import signal
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
from src.models.submission import SubmissionStatus

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
      if submission.status != SubmissionStatus.IN_QUEUE:
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
            update(Submission).values(status=SubmissionStatus.COMPILE_ERROR).
            where((Submission.id == submission_id) & (Submission.status == SubmissionStatus.IN_QUEUE)))
            session.commit()
            return f"Compile error: {compile_result.stderr}"
     
        # get test cases for the problem
         test_cases = session.exec(select(TestCase).where(TestCase.problem_id == submission.problem_id)).all()
         execution_time = 0 
         memory_usage = 0 

        # run the executable with each test case and compare output
         cpu_limit_seconds = max(1, math.ceil(problem.time_limit / 1000))

         def limit_cpu():
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit_seconds, cpu_limit_seconds))

         for test_case in test_cases:
            # run the executable with the test case input
              process = subprocess.Popen(
                [str(exe_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=limit_cpu
            )
              process.stdin.write(test_case.input_data)
              process.stdin.close()
              pid, status, usage = os.wait4(process.pid, 0)
              process.returncode = os.waitstatus_to_exitcode(status)

              # time limit exceeded and runtime error
              if process.returncode < 0:
                sig = -process.returncode

                if sig in (signal.SIGXCPU, signal.SIGKILL):
                    session.exec(
                        update(Submission)
                        .values(status=SubmissionStatus.TIME_LIMIT_EXCEEDED)
                        .where((Submission.id == submission_id) &
                            (Submission.status == SubmissionStatus.IN_QUEUE)))
                    session.commit()
                    return f"Time Limit Exceeded on test: {test_case.id}"

                session.exec(
                    update(Submission)
                    .values(status=SubmissionStatus.RUNTIME_ERROR)
                    .where((Submission.id == submission_id) &
                        (Submission.status == SubmissionStatus.IN_QUEUE))
                )
                session.commit()
                return f"Runtime Error: {test_case.id}"

              # measure execution time and memory usage
              cpu_time = (usage.ru_utime + usage.ru_stime) * 1000
              memory_kb = usage.ru_maxrss/1024.  # to be in MB
              memory_usage = max(memory_usage, memory_kb)
              execution_time = max(execution_time, cpu_time)

              # check time limit exceeded
              if(execution_time > problem.time_limit):
                process.kill()
                session.exec(
                    update(Submission)
                    .values(status=SubmissionStatus.TIME_LIMIT_EXCEEDED)
                    .where((Submission.id == submission_id) & 
                    (Submission.status == SubmissionStatus.IN_QUEUE))
                )
                session.commit()
                return f"Time Limit Exceeded on test: {test_case.id}"

              # check memory limit exceeded
              if(memory_usage > problem.memory_limit):
                session.exec(
                    update(Submission)
                    .values(status=SubmissionStatus.MEMORY_LIMIT_EXCEEDED,
                    execution_time=execution_time,execution_memory=memory_usage)
                    .where((Submission.id == submission_id) & 
                    (Submission.status == SubmissionStatus.IN_QUEUE))
                )
                session.commit()
                return f"Memory Limit Exceeded on test: {test_case.id}"
            
            # todo: measure execution time and include it in the response
            # todo: handle time limit exceeded case and memory limit exceeded case
            # todo : use checker_code and handle exceptions instead of manually checking returncode
            # todo : set test_case number for test_case

               # compare output with expected output
              stdout = process.stdout.read()
              if stdout.strip() != test_case.expected_output.strip():
                    result = session.exec(
                        update(Submission).values(status=SubmissionStatus.WRONG_ANSWER,
                        execution_time=execution_time,execution_memory=memory_usage).
                        where((Submission.id == submission_id) & 
                        (Submission.status == SubmissionStatus.IN_QUEUE)))
                    session.commit()
                    return f"Wrong Answer on test: {test_case.id}"
        
         # if all test cases pass, update submission status to "accepted"
         finalresult = session.exec(
             update(Submission).values(status=SubmissionStatus.ACCEPTED,
             execution_time=execution_time,execution_memory=memory_usage).
             where((Submission.id == submission_id) & 
             (Submission.status == SubmissionStatus.IN_QUEUE)))
         session.commit()
         return "Accepted"

                  



            
