from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init

from background_tasks.utils import init_fastapi_cache
from settings import settings


init_fastapi_cache()

celery = Celery(
    __name__,
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['background_tasks.tasks']
)

@worker_process_init.connect
def configure_worker(**kwargs):
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

celery.autodiscover_tasks()

celery.conf.beat_schedule = {
    'cleanup-unused-links': {
        'task': 'background_tasks.tasks.cleanup_unused_links',
        'schedule': crontab(minute=0, hour=0),
    },
    'set-expired-links': {
        'task': 'background_tasks.tasks.set_expired_links',
        'schedule': 300
    }
}
celery.conf.timezone = 'UTC'
