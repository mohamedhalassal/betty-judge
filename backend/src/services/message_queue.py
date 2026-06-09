from abc import ABC, abstractmethod

class MessageQueue(ABC):
    @abstractmethod
    def send_submission(self, submission_id: int):
        pass