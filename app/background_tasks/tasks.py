import logging

import asyncio

from celery_app import celery
from background_tasks.utils import create_links_service_for_bg_tasks

celery_logger = logging.getLogger(__name__)


@celery.task
def set_expired_links():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    async def _task():
        service = await create_links_service_for_bg_tasks()
        await service.set_expired_links()

    loop.run_until_complete(_task())
    celery_logger.info("Expired links were updated")


@celery.task
def cleanup_unused_links():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    async def _task():
        service = await create_links_service_for_bg_tasks()
        await service.cleanup_unused_links()

    loop.run_until_complete(_task())
    celery_logger.info("Unused links were deleted")
