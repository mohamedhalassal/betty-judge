import os
from azure.storage.queue import QueueClient
import json

def get_queue_client():
     return QueueClient.from_connection_string(
        conn_str=os.getenv("AZURE_QUEUE_CONNECTION_STRING"),
        queue_name=os.getenv("AZURE_QUEUE_NAME")
    )

def send_submission(submission_id: int):
    message = json.dumps({"submission_id": submission_id})
    queue_client = get_queue_client()
    queue_client.send_message(message)