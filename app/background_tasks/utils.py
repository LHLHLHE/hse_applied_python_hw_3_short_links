from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import AsyncSessionFactory
from dependency import get_links_cache_repository
from repository import LinksRepository
from service import LinksService
from settings import settings


def init_fastapi_cache():
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix='links-cache')


@asynccontextmanager
async def get_db_session_for_bg_tasks() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_links_service_for_bg_tasks() -> LinksService:
    async with get_db_session_for_bg_tasks() as session:
        links_repo = LinksRepository(session)
        links_cache = await get_links_cache_repository()
        return LinksService(
            links_repo=links_repo,
            links_cache=links_cache,
            settings=settings
        )
