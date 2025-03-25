from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from dependency import get_users_service
from exceptions import UserAlreadyExistsException
from schemas import UserLoginSchema, UserCreateSchema
from service import UserService

router = APIRouter(prefix='/users', tags=['users'])


@router.post('', response_model=UserLoginSchema)
async def create_user(
    user: UserCreateSchema,
    users_service: Annotated[UserService, Depends(get_users_service)]
):
    try:
        return await users_service.create_user(user)
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )
