import datetime as dt

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import Link
from schemas import LinkCreateSchema, LinkUpdateStatsSchema


class LinksRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_all_links(self) -> list[Link]:
        async with self.db_session as session:
            links: list[Link] = list((await session.execute(select(Link))).scalars().all())
        return links

    async def get_link_by_id(self, link_id: id) -> Link | None:
        async with self.db_session as session:
            link: Link = (
                await session.execute(
                    select(
                        Link
                    ).where(
                        Link.id == link_id,
                        Link.is_expired == False
                    )
                )
            ).scalar_one_or_none()
        return link

    async def get_user_links(self, user_id: int) -> list[Link]:
        async with self.db_session as session:
            links: list[Link] = list((
                 await session.execute(
                     select(
                         Link
                     ).where(
                         Link.user_id == user_id,
                         Link.is_expired == False
                     )
                 )
             ).scalars().all())
        return links

    async def get_link(self, short_code: str) -> Link | None:
        async with self.db_session as session:
            link: Link = (
                await session.execute(
                    select(
                        Link
                    ).where(
                        Link.short_code == short_code,
                        Link.is_expired == False
                    )
                )
            ).scalar_one_or_none()
        return link

    async def get_links_by_original_url(self, original_url: str) -> list[Link]:
        async with self.db_session as session:
            links: list[Link] = list((
                await session.execute(
                    select(
                        Link
                    ).where(
                        Link.original_url == original_url,
                        Link.is_expired == False
                    )
                )
            ).scalars().all())
        return links

    async def get_expired_links(self) -> list[Link]:
        async with self.db_session as session:
            links: list[Link] = list((
                await session.execute(
                    select(
                        Link
                    ).where(
                        Link.is_expired == True
                    )
                )
            ).scalars().all())
        return links

    async def create_link(
        self,
        link: LinkCreateSchema,
        short_code: str,
        short_link: str,
        expires_at: dt.datetime | None,
        user_id: int | None
    ) -> int:
        db_link = Link(
            original_url=link.original_url.unicode_string(),
            short_code=short_code,
            short_link=short_link,
            expires_at=expires_at,
            user_id=user_id,
        )
        async with self.db_session as session:
            session.add(db_link)
            await session.commit()
            await session.flush()
            return db_link.id

    async def delete_link(self, short_code: str) -> None:
        async with self.db_session as session:
            await session.execute(
                delete(
                    Link
                ).where(
                    Link.short_code == short_code
                )
            )
            await session.commit()
            await session.flush()

    async def update_link_stats(self, link_id: int, stats: LinkUpdateStatsSchema) -> None:
        async with self.db_session as session:
            await session.execute(
                update(
                    Link
                ).where(
                    Link.id == link_id
                ).values(
                    redirect_count=stats.redirect_count,
                    last_used_at=stats.last_used_at
                )
            )
            await session.commit()
            await session.flush()

    async def update_link_original_url(self, link_id: int, original_url: str) -> int:
        async with self.db_session as session:
            link_id: int = (
                await session.execute(
                    update(
                        Link
                    ).where(
                        Link.id == link_id
                    ).values(
                        original_url=original_url
                    ).returning(Link.id)
                )
            ).scalar_one_or_none()
            await session.commit()
            await session.flush()
            return link_id

    async def set_expired_links(self):
        async with self.db_session as session:
            expired_links: list[Link] = list((
                await session.execute(
                    update(
                        Link
                    ).where(
                        Link.expires_at < dt.datetime.now(dt.UTC)
                    ).values(
                        is_expired=True
                    ).returning(Link)
                )
            ).scalars().all())
            await session.commit()
            await session.flush()
            return expired_links

    async def delete_unused_links(self, days: int) -> list[Link]:
        time_to_delete = dt.datetime.now(dt.UTC) - dt.timedelta(days=days)
        async with self.db_session as session:
            deleted_links: list[Link] = list((
                await session.execute(
                    delete(
                        Link
                    ).where(
                        ((Link.last_used_at.isnot(None)) & (Link.last_used_at < time_to_delete))
                        | ((Link.last_used_at.is_(None)) & (Link.created_at < time_to_delete))
                    ).returning(Link)
                )
            ).scalars().all())
            await session.commit()
            await session.flush()
            return deleted_links
