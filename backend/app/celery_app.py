from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery = Celery(
    "jogai",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",  # UTC-3 (Brazil)
    enable_utc=True,
    task_track_started=True,
    task_default_queue="jogai",
    worker_concurrency=2,
    worker_prefetch_multiplier=1,
    include=["app.services.channel_poster"],
    broker_connection_retry_on_startup=True,
)

# Beat schedule — all times in America/Sao_Paulo (UTC-3)
celery.conf.beat_schedule = {
    "post-bonus-day": {
        "task": "app.services.channel_poster.task_post_bonus_day",
        "schedule": crontab(hour=9, minute=0),  # 09:00 BRT
    },
    "post-slot-review": {
        "task": "app.services.channel_poster.task_post_slot_review",
        "schedule": crontab(hour=14, minute=0),  # 14:00 BRT
    },
    "post-sport-pick": {
        "task": "app.services.channel_poster.task_post_sport_pick",
        "schedule": crontab(hour=18, minute=0),  # 18:00 BRT
    },
    "deactivate-expired-bonuses": {
        "task": "app.services.channel_poster.task_deactivate_expired",
        "schedule": crontab(minute=0),  # every hour
    },
}
