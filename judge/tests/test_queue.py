import os
import sys
from pathlib import Path

os.environ.setdefault("AZURE_QUEUE_CONNECTION_STRING", "UseDevelopmentStorage=true")
os.environ.setdefault("DATABASE_URL", "sqlite://")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.queues import FakeMessage, FakePoisonQueue, FakeQueue
from src.repository import JudgeSubmissionError
from src import worker


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def expire_all(self):
        pass

    def get(self, model, submission_id):
        return None


def test_non_int_message_is_deleted():
    message = FakeMessage("abc")
    queue = FakeQueue([message])
    poison_queue = FakePoisonQueue()

    worker.handle_message(message, queue, poison_queue)

    assert message in queue.deleted
    assert message not in queue.messages
    assert poison_queue.messages == []


def test_submission_id_not_in_db_stays_in_queue(monkeypatch):
    message = FakeMessage("999")
    queue = FakeQueue([message])
    poison_queue = FakePoisonQueue()

    def fake_judge_submission(session, submission_id):
        raise JudgeSubmissionError(404, "Submission not found")

    monkeypatch.setattr(worker, "get_session", lambda: FakeSession())
    monkeypatch.setattr(worker, "judge_submission", fake_judge_submission)

    worker.handle_message(message, queue, poison_queue)

    assert message not in queue.deleted
    assert message in queue.messages
    assert poison_queue.messages == []


def test_submission_not_in_queue_is_deleted(monkeypatch):
    message = FakeMessage("123")
    queue = FakeQueue([message])
    poison_queue = FakePoisonQueue()

    monkeypatch.setattr(worker, "get_session", lambda: FakeSession())
    monkeypatch.setattr(
        worker,
        "judge_submission",
        lambda session, submission_id: "Submission verdict is not in queue",
    )

    worker.handle_message(message, queue, poison_queue)

    assert message in queue.deleted
    assert message not in queue.messages
    assert poison_queue.messages == []


def test_message_over_retry_limit_goes_to_poison_queue(monkeypatch):
    message = FakeMessage("123", dequeue_count=worker.MAX_QUEUE_DEQUEUE_COUNT + 1)
    queue = FakeQueue([message])
    poison_queue = FakePoisonQueue()

    monkeypatch.setattr(worker, "update_failed_submission_in_database", lambda message: None)

    worker.handle_message(message, queue, poison_queue)

    assert message in queue.deleted
    assert message not in queue.messages
    assert len(poison_queue.messages) == 1
