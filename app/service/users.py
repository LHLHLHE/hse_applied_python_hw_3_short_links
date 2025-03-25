from exceptions import UserAlreadyExistsException
from repository import UsersRepository
from schemas import UserLoginSchema, UserCreateSchema
from service import AuthService


class UserService:
    def __init__(self, user_repo: UsersRepository, auth_service: AuthService):
        self.user_repo = user_repo
        self.auth_service = auth_service

    async def create_user(self, user: UserCreateSchema) -> UserLoginSchema:
        if await self.user_repo.get_user_by_username(user.username):
            raise UserAlreadyExistsException()

        user.password = self.auth_service.get_password_hash(user.password)

        user = await self.user_repo.create_user(user)
        access_token = self.auth_service.generate_access_token(user.id)
        return UserLoginSchema(id=user.id, access_token=access_token)



