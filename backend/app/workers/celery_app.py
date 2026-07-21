import ssl
from celery import Celery

from app.config.settings import settings

# Celery App Initialization
celery = Celery(
    "marketing_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],  # টাস্ক ফাইল রেজিস্ট্রেশন
)

# Celery Configurations (2026 Standards + CrewAI Optimizations)
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Upstash Redis Serverless-এর SSL হ্যান্ডেল করা (Broker এবং Backend উভয়ের জন্য)
if settings.CELERY_BROKER_URL.startswith("rediss://") or settings.CELERY_RESULT_BACKEND.startswith("rediss://"):
    celery.conf.update(
        broker_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
        redis_backend_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
    )