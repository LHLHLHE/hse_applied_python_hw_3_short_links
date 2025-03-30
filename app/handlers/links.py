from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.params import Param
from fastapi.responses import RedirectResponse
from fastapi_cache.decorator import cache
from pydantic import AnyHttpUrl

from dependency import get_links_service, get_request_user_id
from exceptions import (
    LinkNotFound,
    UserIsNotLinkOwner,
    CustomLinkAlreadyExists
)
from repository import LinksCache
from schemas import (
    LinkSchema,
    LinkCreateSchema,
    LinkStatsSchema,
    CreateLinkParams,
    LinkUpdateSchema
)
from service import LinksService

router = APIRouter(prefix='/links', tags=['links'])


@router.get('/expired', response_model=list[LinkSchema])
@cache(
    expire=600,
    namespace='expired_links',
    key_builder=LinksCache.expired_key_builder
)
async def get_expired_links(
    link_service: Annotated[LinksService, Depends(get_links_service)]
):
    return await link_service.get_expired_links()


@router.get('/search', response_model=list[LinkSchema])
@cache(
    expire=600,
    namespace='search_link',
    key_builder=LinksCache.original_url_key_builder
)
async def search_links(
    original_url: Annotated[AnyHttpUrl, Param()],
    link_service: Annotated[LinksService, Depends(get_links_service)],
):
    return await link_service.search_links_by_original_url(original_url)


@router.get('/my', response_model=list[LinkSchema])
@cache(
    expire=600,
    namespace='my_links',
    key_builder=LinksCache.user_id_key_builder
)
async def get_my_links(
    link_service: Annotated[LinksService, Depends(get_links_service)],
    user_id: int | None = Depends(get_request_user_id),
):
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authorized user'
        )
    return await link_service.get_user_links(user_id)


@router.get('/{short_code}/stats', response_model=LinkStatsSchema)
@cache(
    expire=300,
    namespace='link_stats',
    key_builder=LinksCache.short_code_key_builder
)
async def get_link_stats(
    short_code: str,
    link_service: Annotated[LinksService, Depends(get_links_service)]
):
    try:
        return await link_service.get_link_stats(short_code)
    except LinkNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )


@router.post(
    '/shorten',
    response_model=LinkSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_link(
    link: LinkCreateSchema,
    params: Annotated[CreateLinkParams, Param()],
    link_service: Annotated[LinksService, Depends(get_links_service)],
    user_id: int | None = Depends(get_request_user_id),
):
    try:
        return await link_service.create_link(link, params.expires_at, user_id)
    except CustomLinkAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )


@router.get('/{short_code}', response_class=RedirectResponse)
async def redirect_to_original_url(
    short_code: str,
    link_service: Annotated[LinksService, Depends(get_links_service)]
):
    try:
        original_url = await link_service.get_original_url_by_short_code(short_code)
        return RedirectResponse(url=original_url)
    except LinkNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )


@router.delete('/{short_code}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    short_code: str,
    link_service: Annotated[LinksService, Depends(get_links_service)],
    user_id: int | None = Depends(get_request_user_id),
):
    try:
        await link_service.delete_link(short_code, user_id)
    except LinkNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except UserIsNotLinkOwner as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.detail
        )


@router.put('/{short_code}', response_model=LinkSchema)
async def update_link(
    short_code: str,
    data: LinkUpdateSchema,
    link_service: Annotated[LinksService, Depends(get_links_service)],
    user_id: int | None = Depends(get_request_user_id),
):
    try:
        return await link_service.update_link(short_code, data.original_url, user_id)
    except LinkNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except UserIsNotLinkOwner as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.detail
        )
