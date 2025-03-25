import datetime as dt
import random
import string

from fastapi import Request
from pydantic import AnyHttpUrl

from exceptions import (
    LinkNotFound,
    CustomLinkAlreadyExists,
    ShortLinkGenerationException,
    UserIsNotLinkOwner
)
from models import Link
from repository import LinksRepository, LinksCache
from schemas import (
    LinkSchema,
    LinkCreateSchema,
    LinkUpdateStatsSchema,
    LinkStatsSchema
)
from settings import Settings


class LinksService:
    def __init__(
        self,
        links_repo: LinksRepository,
        links_cache: LinksCache,
        settings: Settings,
        request: Request | None = None
    ):
        self.links_repo = links_repo
        self.links_cache = links_cache
        self.settings = settings
        self._resolve_collision_attempt_limit = 5
        self.request = request

    async def create_link(
        self,
        link: LinkCreateSchema,
        expires_at: dt.datetime | None,
        user_id: int | None
    ) -> LinkSchema:
        def _get_short_link() -> str:
            if not self.request:
                raise ShortLinkGenerationException("Request is not provided")

            request_url = str(self.request.url)
            url_parts = request_url.split('/')
            url_parts[-1] = short_code

            return '/'.join(url_parts)

        short_code = await self._generate_short_code(
            custom_token=link.custom_alias
        )

        link_id = await self.links_repo.create_link(
            link=link,
            short_code=short_code,
            short_link=_get_short_link(),
            expires_at=expires_at,
            user_id=user_id
        )
        link = await self.links_repo.get_link_by_id(link_id)
        await self.links_cache.invalidate_link_cache_after_create(link)
        return LinkSchema.model_validate(link)

    async def get_original_url_by_short_code(self, short_code: str) -> str:
        link = await self.links_repo.get_link(short_code)
        if not link:
            raise LinkNotFound()

        await self.links_repo.update_link_stats(
            link_id=link.id,
            stats=LinkUpdateStatsSchema(
                redirect_count=link.redirect_count + 1,
                last_used_at=dt.datetime.now(dt.UTC)
            )
        )

        return link.original_url

    async def delete_link(self, short_code: str, user_id: int | None) -> None:
        link = await self._get_user_link(
            short_code=short_code,
            user_id=user_id
        )
        await self.links_repo.delete_link(short_code=link.short_code)
        await self.links_cache.invalidate_link_cache_after_update_delete(link)

    async def update_link(
        self,
        short_code: str,
        new_original_url: AnyHttpUrl,
        user_id: int | None
    ) -> LinkSchema:
        link = await self._get_user_link(
            short_code=short_code,
            user_id=user_id
        )

        await self.links_repo.update_link_original_url(
            link_id=link.id,
            original_url=new_original_url.unicode_string()
        )
        updated_link = await self.links_repo.get_link_by_id(link.id)
        await self.links_cache.invalidate_link_cache_after_update_delete(updated_link)
        return LinkSchema.model_validate(updated_link)

    async def get_link_stats(self, short_code: str) -> LinkStatsSchema:
        link = await self.links_repo.get_link(short_code)
        if not link:
            raise LinkNotFound()
        return LinkStatsSchema.model_validate(link)

    async def search_links_by_original_url(
        self,
        original_url: AnyHttpUrl
    ) -> list[LinkSchema]:
        links = await self.links_repo.get_links_by_original_url(
            original_url=original_url.unicode_string()
        )
        return [LinkSchema.model_validate(link) for link in links]

    async def get_user_links(self, user_id: int | None) -> list[LinkSchema]:
        links = await self.links_repo.get_user_links(user_id)
        return [LinkSchema.model_validate(link) for link in links]

    async def get_expired_links(self) -> list[LinkSchema]:
        links = await self.links_repo.get_expired_links()
        return [LinkSchema.model_validate(link) for link in links]

    async def set_expired_links(self):
        expired_links = await self.links_repo.set_expired_links()
        if expired_links:
            await self.links_cache.invalidate_link_cache_for_bg_tasks(
                expired_links)

    async def cleanup_unused_links(self):
        deleted_links = await self.links_repo.delete_unused_links(
            self.settings.UNUSED_LINKS_TTL_DAYS
        )
        if deleted_links:
            await self.links_cache.invalidate_link_cache_for_bg_tasks(
                deleted_links)

    def _is_expired(self, link: Link) -> bool:
        if link.expires_at:
            return link.expires_at <= dt.datetime.now(dt.UTC)
        return False

    async def _get_user_link(self, user_id: int | None, short_code: str) -> Link:
        link = await self.links_repo.get_link(short_code=short_code)
        if not link:
            raise LinkNotFound()
        if not user_id or not link.user_id or user_id != link.user_id:
            raise UserIsNotLinkOwner()
        return link

    async def _generate_short_code(self, custom_token: str | None = None) -> str:
        db_links = await self.links_repo.get_all_links()
        short_codes = [link.short_code for link in db_links]
        if custom_token:
            if custom_token in short_codes:
                raise CustomLinkAlreadyExists()
            return custom_token

        attempt = 0
        while attempt < self._resolve_collision_attempt_limit:
            token = self._generate_token()
            if token not in short_codes:
                return token
            attempt += 1

        raise ShortLinkGenerationException(
            "Cannot generate short link after "
            f"{self._resolve_collision_attempt_limit} attempts"
        )

    def _generate_token(self) -> str:
        return ''.join(random.choices(
            string.ascii_letters + string.digits,
            k=self.settings.SHORT_CODE_LENGTH
        ))
