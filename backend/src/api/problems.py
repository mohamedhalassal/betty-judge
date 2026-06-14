from datetime import time
from typing import Annotated
from fastapi import Body, Depends, FastAPI, HTTPException, APIRouter
from sqlmodel import select
from src.models.problem import Problem
from src.schemas.problem import ProblemCreate, ProblemResponse
from src.models.user import User
from src.database import SessionDep, create_db_and_tables
from src.core.security import verify_access_token, get_current_user
router = APIRouter()

# todo: add authentication
# todo : add response models

@router.get("/problems",dependencies=[Depends(verify_access_token)]) #pyright: ignore
def read_problems(session: SessionDep, #pyright: ignore,
 search: str | None = None,
 page: int = 1,
 size: int = 20):
    offset = (page - 1) * size
    statement = select(Problem).order_by(Problem.id)#pyright:ignore
    if search and search.strip():
        statement = statement.where(Problem.name.ilike(f"%{search}%"))#pyright:ignore

    problems = session.exec(statement.offset(offset).limit(size)).all()
    return problems


# todo: add user authentication
# todo: add response model
@router.post("/problems", response_model=ProblemResponse, status_code=201)
async def create_problem(problem: Annotated[ProblemCreate, Body(embed=False)], session: SessionDep,
current_user: Annotated[User, Depends(get_current_user)]):
    problem_db = Problem(name=problem.name,statement=problem.statement,
    created_by=current_user.id,solution=problem.solution,checker_code=problem.checker_code,
    time_limit=problem.time_limit,memory_limit=problem.memory_limit);    #pyright: ignore
    session.add(problem_db)#pyright: ignore
    session.commit()                    #pyright: ignore
    session.refresh(problem_db)#pyright: ignore
    return problem_db


@router.get("/problems/{problem_id}",dependencies=[Depends(verify_access_token)]) #pyright: ignore
def read_problem(problem_id: int, session: SessionDep): #pyright: ignore
    problem = session.exec(select(Problem).where(Problem.id == problem_id)).first()#pyright: ignore
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


# todo : who can delete the problem

@router.delete("/problems/{problem_id}")
def delete_problem(problem_id: int, session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]):
    problem = session.exec(select(Problem).where(Problem.id == problem_id)).first()#pyright: ignore
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this problem")
    session.delete(problem) #pyright: ignore
    session.commit() #pyright: ignore

# todo : who can udpate the problem

@router.patch("/problems/{problem_id}")
def update_problem(problem_id: int, problem: Annotated[ProblemCreate, Body(embed=False)], session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]):
    problem_db = session.exec(select(Problem).where(Problem.id == problem_id)).first()#pyright: ignore
    if not problem_db:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem_db.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this problem")
    problem_db.name = problem.name
    problem_db.statement = problem.statement
    problem_db.solution = problem.solution
    problem_db.checker_code = problem.checker_code
    session.add(problem_db) #pyright: ignore
    session.commit() #pyright: ignore
    session.refresh(problem_db) #pyright: ignore
    return problem_db
