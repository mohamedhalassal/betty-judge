from typing import Annotated
from fastapi import Body, Depends, FastAPI, HTTPException, APIRouter, status
from sqlmodel import select
from src.models.test_case import TestCase
from src.models.problem import Problem
from src.schemas.test_case import TestCaseCreate 
from src.models.user import User
from src.database import SessionDep, create_db_and_tables
from src.core.security import verify_access_token, get_current_user
router = APIRouter()


@router.get("/test_cases") #pyright: ignore
def read_test_cases(session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]):
    if(current_user.is_admin == False):
        raise HTTPException(status_code=403, detail="Not authorized to view test cases")
    statement = select(TestCase).order_by(TestCase.id)#pyright:ignore
    test_cases = session.exec(statement).all()
    return test_cases


@router.get("/test_cases/problem/{problem_id}/samples", dependencies=[Depends(verify_access_token)]) #pyright: ignore
def read_samples_by_problem(problem_id: int, session: SessionDep):
    problem = session.exec(select(Problem).where(Problem.id == problem_id)).first() #pyright: ignore
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    statement = (
        select(TestCase)
        .where(TestCase.problem_id == problem_id)
        .where(TestCase.is_sample == True)
        .order_by(TestCase.id) #pyright: ignore
    )
    test_cases = session.exec(statement).all()
    return test_cases

@router.get("/test_cases/problem/{problem_id}") #pyright: ignore
def read_test_cases_by_problem(problem_id: int, session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]):
    problem = session.exec(select(Problem).where(Problem.id == problem_id)).first() #pyright: ignore
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if(problem.created_by != current_user.id and not current_user.is_admin):
        raise HTTPException(status_code=403, detail="Not authorized to view test cases for this problem")
    statement = (
        select(TestCase)
        .where(TestCase.problem_id == problem_id)
        .order_by(TestCase.id) #pyright: ignore
    )
    test_cases = session.exec(statement).all()
    return test_cases


# todo: add response model
@router.post("/test_cases/problem/{problem_id}", status_code=201) #pyright: ignore   
async def create_test_case(test_case: Annotated[TestCaseCreate, Body(embed=False)], session: SessionDep, problem_id: int,
     current_user: Annotated[User, Depends(get_current_user)]):
     problem = session.exec(select(Problem).where(Problem.id == problem_id)).first()
     if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
     if problem.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to create this test case")
     test_case_db = TestCase(
        input_data=test_case.input_data,
        problem_id=problem_id,
        expected_output=test_case.expected_output,
        is_sample=test_case.is_sample)  #pyright: ignore
     session.add(test_case_db)  #pyright: ignore
     session.commit()  #pyright: ignore
     session.refresh(test_case_db)  #pyright: ignore
     return test_case_db


@router.get("/test_cases/{test_case_id}") #pyright: ignore
def read_test_case(test_case_id: int, session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)]): #pyright: ignore
    test_case = session.exec(select(TestCase).where(TestCase.id == test_case_id)).first()#pyright: ignore
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    problem = session.exec(select(Problem).where(Problem.id == test_case.problem_id)).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this test case")
   
    return test_case


# todo : who can delete the test_case

@router.delete("/test_cases/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case(test_case_id: int, session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]):
    test_case = session.exec(select(TestCase).where(TestCase.id == test_case_id)).first()#pyright: ignore
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    problem = session.exec(select(Problem).where(Problem.id == test_case.problem_id)).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this test case")
    session.delete(test_case) #pyright: ignore
    session.commit() #pyright: ignore
    
# todo : who can update the test_case

@router.patch("/test_cases/{test_case_id}", dependencies=[Depends(verify_access_token)])
def update_test_case(test_case_id: int, test_case: Annotated[TestCaseCreate, Body(embed=False)], session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]):
    test_case_db = session.exec(select(TestCase).where(TestCase.id == test_case_id)).first()#pyright: ignore
    if not test_case_db:
        raise HTTPException(status_code=404, detail="Test case not found")
    problem = session.exec(select(Problem).where(Problem.id == test_case_db.problem_id)).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    if problem.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this test case")
 
    test_case_db.input_data = test_case.input_data
    test_case_db.expected_output = test_case.expected_output
    test_case_db.is_sample = test_case.is_sample
    session.add(test_case_db) #pyright: ignore
    session.commit() #pyright: ignore
    session.refresh(test_case_db) #pyright: ignore
    return test_case_db
