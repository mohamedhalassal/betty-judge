from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, select
from sqlmodel.pool import StaticPool
from src.models.submission import Submission
from src.models.user import User
from src.models.problem import Problem
from src.models.test_case import TestCase
from src.models.submission import SubmissionStatus
from src.runner import add_testcase_result, get_session
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


def create_test_submission(
    session,
    user,
    problem_id,
    source_code,
    verdict=SubmissionStatus.IN_QUEUE,
):
    submission = Submission(
        user_id=user.id,
        problem_id=problem_id,
        source_code=source_code,
        verdict=verdict,
    )
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission


def test_accepted_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a+b;}",
        )
        create_response = run_judge(session, submission.id)
        assert create_response.status_code == 201
        assert create_response.json() == "Accepted"


def test_add_testcase_result_includes_test_case_id():
    testcases = []
    test_case = TestCase(
        id=123,
        problem_id=456,
        input_data="2 3",
        expected_output="5",
        is_sample=False,
    )

    add_testcase_result(testcases, 1, test_case, "passed", 2.5, 1.25)

    assert testcases == [
        {
            "id": 123,
            "number": 1,
            "status": "passed",
            "time_ms": 2.5,
            "memory_mb": 1.25,
        }
    ]


def test_wrong_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a+b+b;}",
        )
        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)
        assert create_response.status_code == 201
        assert create_response.json() == f"Wrong Answer on test: {test_case.id}"
        assert updated_submission.execution_time is not None
        assert updated_submission.execution_memory is not None


def test_compilation_error_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\nint main(){int a,b std::cin>>a>>b; std::cout<<a+b;}",  # forget ;
        )
        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)
        assert create_response.status_code == 201
        assert create_response.json().startswith("Compile error")
        assert updated_submission.execution_time == 0
        assert updated_submission.execution_memory == 0


def test_runtime_error_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <vector>\nint main(){ std::vector<int> a(3); return a.at(10); }",
        )
        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)
        assert create_response.status_code == 201
        assert create_response.json() == f"Runtime Error on test: {test_case.id}"
        assert updated_submission.execution_time is not None
        assert updated_submission.execution_memory is not None


def test_time_limit_exceeded_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\nint main(){int a,b; std::cin>>a>>b; for(int i=0;i<1e10;i++); std::cout<<a+b;}",
        )
        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)
        assert create_response.status_code == 201
        assert create_response.json() == f"Time Limit Exceeded on test: {test_case.id}"
        assert updated_submission.execution_time == problem.time_limit
        assert updated_submission.execution_memory is not None


def test_infinity_loop_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\nint main(){int a,b; std::cin>>a>>b; for(int i=0;;i++); std::cout<<a+b;}",
        )
        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)
        assert create_response.status_code == 201
        assert create_response.json() == f"Time Limit Exceeded on test: {test_case.id}"
        assert updated_submission.execution_time == problem.time_limit
        assert updated_submission.execution_memory is not None




def test_infinity_sleep_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\n #include <unistd.h>\n int main(){int a,b; std::cin>>a>>b; for(int i=0;;i++)sleep(1); std::cout<<a+b;}",
        )
        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)
        assert create_response.status_code == 201
        assert create_response.json() == f"Idleness Limit Exceeded on test: {test_case.id}"
        assert updated_submission.execution_time is not None
        assert updated_submission.execution_memory is not None


def test_Ideleness_limit_exceeded_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\n#include <unistd.h>\n int arr[100000000];int main(){int a,b;sleep(20); std::cin>>a>>b;for(int i=0;i<100000000;i++)arr[i]=i; std::cout<<a+b;}",
        )
        create_response = run_judge(session, submission.id)
        assert create_response.status_code == 201
        assert (
            create_response.json() == f"Idleness Limit Exceeded on test: {test_case.id}"
        )
def test_infinity_input_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\nint main(){int x; while(true){std::cin>>x;}}",
        )
        create_response = run_judge(session, submission.id)
        assert create_response.status_code == 201
        assert create_response.json() == f"Time Limit Exceeded on test: {test_case.id}"


def test_Infinite_output_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\nint main(){int a,b;std::cin>>a>>b;for(int i=0;;i++)std::cout<<a+b;}",
        )
        create_response = run_judge(session, submission.id)
        assert create_response.status_code == 201
        assert (
            create_response.json()
            in (
                f"Idleness Limit Exceeded on test: {test_case.id}",
                f"Time Limit Exceeded on test: {test_case.id}",
            )
        )


def test_memory_limit_exceeded_solution():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        test_case = create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            source_code="#include <iostream>\n int arr[100000000];int main(){int a,b; std::cin>>a>>b;for(int i=0;i<100000000;i++)arr[i]=i; std::cout<<a+b;}",
        )
        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)
        assert create_response.status_code == 201
        assert (
            create_response.json() == f"Memory Limit Exceeded on test: {test_case.id}"
        )
        assert updated_submission.execution_time is not None
        assert updated_submission.execution_memory == problem.memory_limit


def test_submission_not_found():
    with Session(engine) as session:
        create_response = run_judge(session, 999)

    assert create_response.status_code == 404
    assert create_response.json()["detail"] == "Submission not found"


def test_submission_verdict_not_in_queue():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            "#include <iostream>\nint main(){std::cout<<1;}",
            verdict=SubmissionStatus.ACCEPTED,
        )

        create_response = run_judge(session, submission.id)

        assert create_response.status_code == 400
        assert create_response.json()["detail"] == "Submission verdict is not in queue"


def test_problem_not_found():
    with Session(engine) as session:
        user = create_test_user(session)
        submission = create_test_submission(
            session,
            user,
            999,
            "#include <iostream>\nint main(){std::cout<<1;}",
        )

        create_response = run_judge(session, submission.id)

        assert create_response.status_code == 404
        assert create_response.json()["detail"] == "Problem not found"


def test_wrong_answer_reports_first_failing_test_case():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        first_case = create_test_case(session, problem, "2 3", "5", False)
        second_case = create_test_case(session, problem, "4 6", "11", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            "#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a+b;}",
        )

        create_response = run_judge(session, submission.id)

        assert create_response.status_code == 201
        assert create_response.json() == f"Wrong Answer on test: {second_case.id}"
        assert create_response.json() != f"Wrong Answer on test: {first_case.id}"


def test_accepted_solution_updates_submission_metrics():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            "#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a+b;}",
        )

        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)

        assert create_response.status_code == 201
        assert create_response.json() == "Accepted"
        assert updated_submission.verdict == SubmissionStatus.ACCEPTED
        assert updated_submission.execution_time is not None
        assert updated_submission.execution_memory is not None


def test_wrong_answer_updates_submission_verdict():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            "#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<a+b+b;}",
        )

        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)

        assert create_response.status_code == 201
        assert updated_submission.verdict == SubmissionStatus.WRONG_ANSWER


def test_compile_error_updates_submission_verdict():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            "#include <iostream>\nint main(){int a,b std::cin>>a>>b; std::cout<<a+b;}",
        )

        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)

        assert create_response.status_code == 201
        assert updated_submission.verdict == SubmissionStatus.COMPILE_ERROR


def test_output_comparison_ignores_outer_whitespace():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        create_test_case(session, problem, "2 3", "5", False)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            "#include <iostream>\nint main(){int a,b; std::cin>>a>>b; std::cout<<\"\\n\"<<a+b<<\"\\n\\n\";}",
        )

        create_response = run_judge(session, submission.id)

        assert create_response.status_code == 201
        assert create_response.json() == "Accepted"


def test_problem_with_no_test_cases_is_accepted():
    with Session(engine) as session:
        user = create_test_user(session)
        problem = create_test_problem(session, user)
        submission = create_test_submission(
            session,
            user,
            problem.id,
            "#include <iostream>\nint main(){std::cout<<1;}",
        )

        create_response = run_judge(session, submission.id)
        session.expire_all()
        updated_submission = session.get(Submission, submission.id)

        assert create_response.status_code == 201
        assert create_response.json() == "Accepted"
        assert updated_submission.verdict == SubmissionStatus.ACCEPTED
