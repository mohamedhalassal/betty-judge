import json
import os
import socket
import time
from azure.storage.queue import QueueClient
from src.judge import judge_submission
from src.repository import JudgeSubmissionError
from src.database import get_session
from src.models.submission import Submission
from src.repository import finish_submission
from src.verdict import VerdictResult
from src.models.submission import SubmissionStatus
from src.queues import AzurePoisonQueue, AzureQueue, Queue, PoisonQueue

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
    message_content: str, dequeue_count: int, poison_queue: PoisonQueue
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

def update_failed_submission_in_database(message):
    try:
        submission_id = int(message.content)
        with get_session() as session:
            finish_submission(
                session=session,
                submission_id=submission_id,
                Verdict_result=VerdictResult(
                    verdict=SubmissionStatus.FAILED,
                    message="Submission moved to poison queue after multiple failed attempts",
                    execution_time=0,
                    execution_memory=0,
                ),
            )
    except ValueError:
        print(
            f"[{WORKER_NAME}] poison message has invalid submission id: {message.content}",
            flush=True,
        )
    except Exception as exc:
        print(
            f"[{WORKER_NAME}] failed to mark submission {message.content} as failed: {exc}",
            flush=True,
        )
    
def handle_message(message, queue: Queue, poison_queue: PoisonQueue,get_session_func=get_session
,judge_submission_func=judge_submission,update_failed_submission_in_database_func=update_failed_submission_in_database):
    dequeue_count = getattr(message, "dequeue_count", 1) or 1
    if dequeue_count > MAX_QUEUE_DEQUEUE_COUNT:
        update_failed_submission_in_database_func(message)
        push_submission_to_poison_queue(message.content, dequeue_count, poison_queue)
        queue.delete_message(message)
        return
    try:
        submission_id = int(message.content)
        print(
            f"[{WORKER_NAME}] took submission {submission_id}",
            flush=True,
        )
        with get_session_func() as session:
            judge_submission_func(session, submission_id)
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
        print(
            f"[{WORKER_NAME}] leaving message {message.content} in queue for retry",
            flush=True,
        )
    except Exception as exc:
        print(
            f"[{WORKER_NAME}] failed submission message {message.content}: {exc}",
            flush=True,
        )
        print(
            f"[{WORKER_NAME}] leaving message {message.content} in queue for retry",
            flush=True,
        )


def create_azure_queue():
    client = QueueClient.from_connection_string(
        AZURE_QUEUE_CONNECTION_STRING,
        queue_name=AZURE_QUEUE_NAME,
    )
    return AzureQueue(client)


def create_azure_poison_queue():
    client = QueueClient.from_connection_string(
        AZURE_QUEUE_CONNECTION_STRING,
        queue_name=AZURE_POISON_QUEUE_NAME,
    )
    return AzurePoisonQueue(client)


def run_worker():
    queue = create_azure_queue()
    poison_queue = create_azure_poison_queue()

    while True:
        received_any = False
        messages = queue.receive_messages()
        for message in messages:
            received_any = True
            handle_message(message, queue, poison_queue)
        if not received_any:
            time.sleep(1)
