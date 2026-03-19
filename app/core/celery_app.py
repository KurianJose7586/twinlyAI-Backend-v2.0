from celery import Celery
import platform
from app.core.config import settings

celery_app = Celery(
    "twinlyai_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Windows does not reliably support Celery's default prefork pool.
# Use solo for stable local development on Windows.
if platform.system().lower() == "windows":
    celery_app.conf.worker_pool = "solo"
    celery_app.conf.worker_concurrency = 1

# Optional: define beat schedule here for fallback syncs
celery_app.conf.beat_schedule = {
    # 'sync-github-repos-every-hour': {
    #     'task': 'app.worker.tasks.sync_all_repos',
    #     'schedule': 3600.0,
    # },
}
