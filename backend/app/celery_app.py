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
    include=["app.services.channel_poster", "app.services.digest_builder", "app.services.bonus_parser"],
    broker_connection_retry_on_startup=True,
)

# Beat schedule — all times in America/Sao_Paulo (UTC-3)
celery.conf.beat_schedule = {
    "post-bonus-day": {
        "task": "app.services.channel_poster.task_post_bonus_day",
        "schedule": crontab(hour=9, minute=0),  # 09:00 BRT
    },
    # "post-slot-review" — disabled until real slot data source is integrated
    # Static RTP data is dangerous for users making financial decisions
    "post-sport-pick": {
        "task": "app.services.channel_poster.task_post_sport_pick",
        "schedule": crontab(hour=18, minute=0),  # 18:00 BRT
    },
    "deactivate-expired-bonuses": {
        "task": "app.services.channel_poster.task_deactivate_expired",
        "schedule": crontab(minute=0),  # every hour
    },
    "send-daily-digest": {
        "task": "app.services.digest_builder.task_send_digest",
        "schedule": crontab(hour=8, minute=0),  # 08:00 BRT
    },
    "parse-bonuses": {
        "task": "app.services.bonus_parser.task_parse_bonuses",
        "schedule": crontab(minute=0, hour="*/6"),  # every 6 hours
    },
}
