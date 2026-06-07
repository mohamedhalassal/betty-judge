import json

from src.services.queue_service import send_submission


def test_send_submission(monkeypatch):

    sent_messages = []

    class FakeQueueClient:
        def send_message(self, message):
            sent_messages.append(message)

    monkeypatch.setattr(
        "src.services.queue_service.get_queue_client",
        lambda: FakeQueueClient(),
    )

    send_submission(123)

    assert len(sent_messages) == 1

    assert json.loads(sent_messages[0]) == {
        "submission_id": 123
    }

