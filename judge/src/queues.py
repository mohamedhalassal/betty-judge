from abc import ABC, abstractmethod


class Queue(ABC):
    @abstractmethod
    def receive_messages(self):
        pass

    @abstractmethod
    def delete_message(self, message):
        pass


class PoisonQueue(ABC):
    @abstractmethod
    def send_message(self, message):
        pass


class AzureQueue(Queue):
    def __init__(self, client):
        self.client = client

    def receive_messages(self):
        return self.client.receive_messages(messages_per_page=1, visibility_timeout=300)

    def delete_message(self, message):
        self.client.delete_message(message)


class AzurePoisonQueue(PoisonQueue):
    def __init__(self, client):
        self.client = client

    def send_message(self, message):
        self.client.send_message(message)


class FakeMessage:
    def __init__(self, content, dequeue_count=1):
        self.content = content
        self.dequeue_count = dequeue_count


class FakeQueue(Queue):
    def __init__(self, messages):
        self.messages = messages
        self.deleted = []

    def receive_messages(self):
        return self.messages

    def delete_message(self, message):
        self.deleted.append(message)
        self.messages.remove(message)


class FakePoisonQueue(PoisonQueue):
    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)