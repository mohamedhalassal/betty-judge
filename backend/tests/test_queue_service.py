import json

from src.services.queue_service import AzureQueueService


def test_send_submission():

    sent_messages = []

    class FakeQueueClient:
        def send_message(self, message):
            sent_messages.append(message)

    service = FakeQueueClient()

    service.send_submission(123)

    assert len(sent_messages) == 1

    assert json.loads(sent_messages[0]) == {
        "submission_id": 123
    }
