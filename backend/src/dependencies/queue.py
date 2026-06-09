from src.services.queue_service import AzureQueueService

def get_queue_service():
    return AzureQueueService()