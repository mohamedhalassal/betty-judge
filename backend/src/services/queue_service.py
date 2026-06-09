import os
import json
from azure.storage.queue import QueueClient
from src.services.message_queue import MessageQueue


class AzureQueueService(MessageQueue):
    def __init__(self):
        self.client = QueueClient.from_connection_string(
            conn_str=os.getenv("AZURE_QUEUE_CONNECTION_STRING"),
            queue_name=os.getenv("AZURE_QUEUE_NAME")
        )
    def send_submission(self, submission_id: int):
        message = json.dumps({"submission_id": submission_id})
        self.client.send_message(message)
