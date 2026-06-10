import json
import os
import socket
import time
from azure.core.exceptions import ResourceExistsError
from azure.storage.queue import QueueClient
from src.judge import judge_submission
from src.repository import JudgeSubmissionError
from src.database import get_session
from src.models.submission import Submission

WORKER_NAME = os.getenv("WORKER_NAME") or socket.gethostname()
AZURE_QUEUE_NAME = os.getenv("AZURE_QUEUE_NAME", "quickstartqueuesample")
AZURE_POISON_QUEUE_NAME = os.getenv(
    "AZURE_POISON_QUEUE_NAME", f"{AZURE_QUEUE_NAME}-poison"
)
AZURE_QUEUE_CONNECTION_STRING = os.getenv("AZURE_QUEUE_CONNECTION_STRING")
if not AZURE_QUEUE_CONNECTION_STRING:
    raise RuntimeError("AZURE_QUEUE_CONNECTION_STRING must be set in backend/.env")
MAX_QUEUE_DEQUEUE_COUNT = int(os.getenv("MAX_QUEUE_DEQUEUE_COUNT", "5"))
from src.verdict import verdict_value

def push_submission_to_poison_queue(
    message_content: str,
    dequeue_count: int,
    poison_queue: QueueClient
):
    poison_payload = {
                "content": message_content,
                "dequeue_count": dequeue_count,
                "source_queue": AZURE_QUEUE_NAME,
                "worker": WORKER_NAME,
            }
    poison_queue.send_message(json.dumps(poison_payload))
    print(
        f"[{WORKER_NAME}] moved poison message {message_content} "
        f"to {AZURE_POISON_QUEUE_NAME} after {dequeue_count - 1} failed attempt(s)",
        flush=True,
    )

def run_worker():
    queue = QueueClient.from_connection_string(
        AZURE_QUEUE_CONNECTION_STRING,
        queue_name=AZURE_QUEUE_NAME,
    )
    poison_queue = QueueClient.from_connection_string(
        AZURE_QUEUE_CONNECTION_STRING,
        queue_name=AZURE_POISON_QUEUE_NAME,
    )
    try:
        poison_queue.create_queue()
    except ResourceExistsError:
        pass
    print(
        f"Judge worker {WORKER_NAME} listening on queue {AZURE_QUEUE_NAME}",
        flush=True,
    )

    while True:
        received_any = False
        messages = queue.receive_messages(messages_per_page=1, visibility_timeout=300)
        for message in messages:
            received_any = True
            dequeue_count = getattr(message, "dequeue_count", 1) or 1
            if dequeue_count > MAX_QUEUE_DEQUEUE_COUNT:
                push_submission_to_poison_queue(message.content, dequeue_count, poison_queue)  
                queue.delete_message(message)
                continue
            try:
                submission_id = int(message.content)
                print(
                    f"[{WORKER_NAME}] took submission {submission_id}",
                    flush=True,
                )
                with get_session() as session:
                    judge_submission(session, submission_id)
                    session.expire_all()
                    judged_submission = session.get(Submission, submission_id)
                    verdict = judged_submission.verdict if judged_submission else None
                    print(
                        f"[{WORKER_NAME}] finished submission {submission_id} "
                        f"verdict={verdict_value(verdict)}",
                        flush=True,
                    )
                queue.delete_message(message)
            except ValueError:
                print(
                    f"[{WORKER_NAME}] invalid submission id in message: {message.content}",
                    flush=True,
                )
                queue.delete_message(message)
            except JudgeSubmissionError as exc:
                print(
                    f"[{WORKER_NAME}] skipped submission: {exc.status_code} {exc.detail}",
                    flush=True,
                )
                if exc.detail in ("Submission not found", "Problem not found"):
                    print(
                        f"[{WORKER_NAME}] leaving message {message.content} in queue for retry",
                        flush=True,
                    )
                else:
                    queue.delete_message(message)
            except Exception as exc:
                print(
                    f"[{WORKER_NAME}] failed submission message {message.content}: {exc}",
                    flush=True,
                )

        if not received_any:
            time.sleep(1)