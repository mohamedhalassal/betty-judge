import os
from azure.storage.queue import QueueClient
import json

queue_client = QueueClient.from_connection_string(
    conn_str=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="submission",
)

def send_submission(submission_id: int):
    message = json.dumps({"submission_id": submission_id})
    queue_client.send_message(message)  