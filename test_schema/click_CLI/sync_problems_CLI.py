import os
from collections import defaultdict
from sqlmodel import Session, select, create_engine
from models.problem import Problem
from models.test_case import TestCase
from backend_client import create_problem
import click
from database import get_engine


def sync_problems():
    with Session(get_engine()) as session:
        rows = session.exec(
            select(Problem,  TestCase).where(Problem.revision_id == None)
            .where(Problem.id is not None)
            .join(TestCase, Problem.id == TestCase.problem_id)
        ).all()
        problems_with_cases: defaultdict[int, list[TestCase]] = defaultdict(list)
        problems_by_id: dict[int, Problem] = {}

        for problem, test_case in rows:
            assert problem.id is not None, "Problem ID should not be None"
            problems_by_id[problem.id] = problem
            
            problems_with_cases[problem.id].append(test_case)       
        for (problem_id_, test_cases) in problems_with_cases.items():
            try:
                problem = problems_by_id[problem_id_]
                assert problem.id is not None, "Problem ID should not be None"
                revision_id = create_problem(problem, test_cases)
                problem.revision_id = revision_id
                session.add(problem)
            except Exception as e:
                assert problem.id is not None, "Problem ID should not be None"
                print(f"Failed to create problem {problem.id} in backend: {e}")
                continue
        session.commit()

@click.command()
def main():
	click.echo("Syncing problems...")
	sync_problems()
	click.echo("Problems sync finished.")

if __name__ == "__main__":
    main()
