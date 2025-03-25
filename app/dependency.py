import httpx
from fastapi import Depends, security, Security, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db_session
from exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    UserNotFound
)
from repository import LinksRepository, UsersRepository, LinksCache
from security import reusable_oauth2
from service import LinksService, AuthService, UserService
from settings import settings


async def get_links_repository(
    db_session: AsyncSession = Depends(get_db_session)
) -> LinksRepository:
    return LinksRepository(db_session)


async def get_links_cache_repository() -> LinksCache:
    return LinksCache()


async def get_links_service(
    request: Request,
    links_repo: LinksRepository = Depends(get_links_repository),
    links_cache: LinksCache = Depends(get_links_cache_repository),
) -> LinksService:
    return LinksService(
        links_repo=links_repo,
        links_cache=links_cache,
        settings=settings,
        request=request,
    )


async def get_users_repository(
    db_session: AsyncSession = Depends(get_db_session)
) -> UsersRepository:
    return UsersRepository(db_session)


async def get_async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient()


async def get_auth_service(
    users_repo: UsersRepository = Depends(get_users_repository)
) -> AuthService:
    return AuthService(
        user_repo=users_repo,
        settings=settings
    )


async def get_users_service(
    users_repo: UsersRepository = Depends(get_users_repository),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserService:
    return UserService(user_repo=users_repo, auth_service=auth_service)


async def get_request_user_id(
    auth_service: AuthService = Depends(get_auth_service),
    token: security.http.HTTPAuthorizationCredentials | None = Security(reusable_oauth2)
) -> int | None:
    if not token:
        return None

    try:
        return auth_service.get_user_id_from_access_token(token.credentials)
    except (TokenExpiredException, InvalidTokenException, UserNotFound) as e:
        raise HTTPException(
            status_code=401,
            detail=e.detail
        )
