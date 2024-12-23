from celery import Celery

# Initialize Celery with Redis as the broker
celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",  # Redis server URL
    backend="redis://localhost:6379/0",  # Redis server backend for storing task results
)

celery.conf.result_expires = 3600  # Task result expiration in seconds
