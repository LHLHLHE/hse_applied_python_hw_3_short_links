from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from dependency import get_auth_service
from exceptions import UserNotFound, UserIncorrectPasswordException
from schemas import UserLoginSchema, UserCreateSchema
from service import AuthService

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/login', response_model=UserLoginSchema)
async def login(
    user: UserCreateSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    try:
        return await auth_service.login(user.username, user.password)
    except UserNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except UserIncorrectPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.detail
        )
