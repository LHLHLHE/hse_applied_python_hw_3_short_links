from fastapi_cache import FastAPICache

from models import Link


class LinksCache:
    def __init__(self):
        self._redis = FastAPICache.get_backend()
        self.prefix = FastAPICache.get_prefix()

    @staticmethod
    def short_code_key_builder(func, namespace: str = "", *args, **kwargs):
        short_code = kwargs['kwargs']['short_code']
        return f'{namespace}:{short_code}'

    @staticmethod
    def expired_key_builder(func, namespace: str = "", *args, **kwargs):
        return f'{namespace}:{func.__module__}:{func.__name__}'

    @staticmethod
    def original_url_key_builder(func, namespace: str = "", *args, **kwargs):
        original_url = kwargs['kwargs']['original_url']
        return f'{namespace}:{original_url}'

    @staticmethod
    def user_id_key_builder(func, namespace: str = "", *args, **kwargs):
        user_id = kwargs['kwargs']['user_id']
        return f'{namespace}:{user_id}'

    async def invalidate_search_link_cache(self, original_url: str):
        await self._redis.clear(f'{self.prefix}:search_link', original_url)

    async def invalidate_my_links_cache(self, user_id: int):
        await self._redis.clear(f'{self.prefix}:my_links', str(user_id))

    async def invalidate_link_stats_cache(self, short_code: str):
        await self._redis.clear(f'{self.prefix}:link_stats', short_code)

    async def invalidate_expired_links_cache(self):
        await self._redis.clear(f'{self.prefix}:expired_links')

    async def invalidate_link_cache_after_create(self, link: Link):
        await self.invalidate_search_link_cache(link.original_url)
        await self.invalidate_my_links_cache(link.user_id)

    async def invalidate_link_cache_after_update_delete(self, link: Link):
        await self.invalidate_link_stats_cache(link.short_code)
        await self.invalidate_search_link_cache(link.original_url)
        await self.invalidate_my_links_cache(link.user_id)

    async def invalidate_link_cache_for_bg_tasks(self, links: list[Link]):
        await self.invalidate_expired_links_cache()
        for user_id in set([link.user_id for link in links]):
            await self.invalidate_my_links_cache(user_id)
        for link in links:
            await self.invalidate_link_stats_cache(link.short_code)
            await self.invalidate_search_link_cache(link.original_url)
