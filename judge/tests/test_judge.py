from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool
from src.models.submission import Submission
from src.models.user import User
from src.models.problem import Problem
from src.models.test_case import TestCase
from src.models.submission import SubmissionStatus
from src.runner import get_session
from main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_session():
    with Session(engine) as session:
        yield session


client = TestClient(app)


def setup_function():
    SQLModel.metadata.create_all(engine)
    app.dependency_overrides[get_session] = get_test_session


def teardown_function():
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


def create_test_user(session):
    user = User(
        username="testuser",
        email="test@example.com",
        google_id="google-123",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_test_problem(session, user, name="Two Sum"):
    problem = Problem(
        name=name,
        statement="Sample statement",
        created_by=user.id,
        solution="Sample solution",
        checker_code="Sample checker code",
        time_limit=2000,
        memory_limit=100,  # 100 MB
    )
    session.add(problem)
    session.commit()
    session.refresh(problem)
    return problem


def create_test_case(session, problem, input_data, expected_output, is_sample):
    test_case = TestCase(
        input_data=input_data,
        expected_output=expected_output,
        is_sample=is_sample,
        problem_id=problem.id,
    )
    session.add(test_case)
    session.commit()
    session.refresh(test_case)
    return test_case


def test_accepted_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = Submission(
            id=1,
            user_id=user.id,
            problem_id=problem_id,
            source_code="#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a+b;}",
            verdict=SubmissionStatus.IN_QUEUE,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        create_response = client.post(f"/runner?submission_id={submission.id}")
        assert create_response.status_code == 201
        assert create_response.json() == "Accepted"


def test_wrong_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = Submission(
            id=1,
            user_id=user.id,
            problem_id=problem_id,
            source_code="#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a+b+b;}",
            verdict=SubmissionStatus.IN_QUEUE,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        create_response = client.post(f"/runner?submission_id={submission.id}")
        assert create_response.status_code == 201
        assert create_response.json() == f"Wrong Answer on test: {test_case.id}"


def test_compilation_error_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = Submission(
            id=1,
            user_id=user.id,
            problem_id=problem_id,
            source_code="#include <iostream>\nint main(){int a,b std::cin>>a>>b; std::cout<<a+b;}",  # forget ;
            verdict=SubmissionStatus.IN_QUEUE,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        create_response = client.post(f"/runner?submission_id={submission.id}")
        assert create_response.status_code == 201
        assert create_response.json().startswith("Compile error")


def test_runtime_error_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = Submission(
            id=1,
            user_id=user.id,
            problem_id=problem_id,
            source_code="#include <vector>\nint main(){ std::vector<int> a(3); return a.at(10); }",
            verdict=SubmissionStatus.IN_QUEUE,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        create_response = client.post(f"/runner?submission_id={submission.id}")
        assert create_response.status_code == 201
        assert create_response.json() == f"Runtime Error on test: {test_case.id}"


def test_time_limit_exceeded_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = Submission(
            id=1,
            user_id=user.id,
            problem_id=problem_id,
            source_code="#include <iostream>\nint main(){int a,b; std::cin>>a>>b; for(int i=0;i<1e10;i++); std::cout<<a+b;}",
            verdict=SubmissionStatus.IN_QUEUE,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        create_response = client.post(f"/runner?submission_id={submission.id}")
        assert create_response.status_code == 201
        assert create_response.json() == f"Time Limit Exceeded on test: {test_case.id}"


def test_infinity_loop_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = Submission(
            id=1,
            user_id=user.id,
            problem_id=problem_id,
            source_code="#include <iostream>\nint main(){int a,b; std::cin>>a>>b; for(int i=0;;i++); std::cout<<a+b;}",
            verdict=SubmissionStatus.IN_QUEUE,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        create_response = client.post(f"/runner?submission_id={submission.id}")
        assert create_response.status_code == 201
        assert create_response.json() == f"Time Limit Exceeded on test: {test_case.id}"


def test_infinity_sleep_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = Submission(
            id=1,
            user_id=user.id,
            problem_id=problem_id,
            source_code="#include <iostream>\n #include <unistd.h>\n int main(){int a,b; std::cin>>a>>b; for(int i=0;;i++)sleep(1); std::cout<<a+b;}",
            verdict=SubmissionStatus.IN_QUEUE,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        create_response = client.post(f"/runner?submission_id={submission.id}")
        assert create_response.status_code == 201
        assert create_response.json() == f"Idleness Limit Exceeded on test: {test_case.id}"


def test_Ideleness_limit_exceeded_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = Submission(
            id=1,
            user_id=user.id,
            problem_id=problem_id,
            source_code="#include <iostream>\n#include <unistd.h>\n int arr[100000000];int main(){int a,b;sleep(20); std::cin>>a>>b;for(int i=0;i<100000000;i++)arr[i]=i; std::cout<<a+b;}",
            verdict=SubmissionStatus.IN_QUEUE,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        create_response = client.post(f"/runner?submission_id={submission.id}")
        assert create_response.status_code == 201
        assert (
            create_response.json() == f"Idleness Limit Exceeded on test: {test_case.id}"
        )


def test_memory_limit_exceeded_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        problem_id = problem.id
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = Submission(
            id=1,
            user_id=user.id,
            problem_id=problem_id,
            source_code="#include <iostream>\n int arr[100000000];int main(){int a,b; std::cin>>a>>b;for(int i=0;i<100000000;i++)arr[i]=i; std::cout<<a+b;}",
            verdict=SubmissionStatus.IN_QUEUE,
        )
        session.add(submission)
        session.commit()
        session.refresh(submission)
        create_response = client.post(f"/runner?submission_id={submission.id}")
        assert create_response.status_code == 201
        assert (
            create_response.json() == f"Memory Limit Exceeded on test: {test_case.id}"
        )
