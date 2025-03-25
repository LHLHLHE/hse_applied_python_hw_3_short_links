import datetime as dt

from jose import jwt, JWTError

from exceptions import (
    UserNotFound,
    UserIncorrectPasswordException,
    TokenExpiredException,
    InvalidTokenException
)
from models import User
from repository import UsersRepository
from schemas import UserLoginSchema
from security import pwd_context
from settings import Settings


class AuthService:
    def __init__(self, user_repo: UsersRepository, settings: Settings):
        self.user_repo = user_repo
        self.settings = settings

    async def login(self, username: str, password: str) -> UserLoginSchema:
        user = await self.user_repo.get_user_by_username(username)
        self._validate_auth_user(user, password)
        access_token = self.generate_access_token(user.id)
        return UserLoginSchema(id=user.id, access_token=access_token)

    def _validate_auth_user(self, user: User, password: str):
        if not user:
            raise UserNotFound()
        if not self.verify_password(password, user.password):
            raise UserIncorrectPasswordException()

    def generate_access_token(self, user_id: int) -> str:
        expires_date_unix = (
            dt.datetime.now(dt.UTC)
            + dt.timedelta(minutes=self.settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        ).timestamp()
        return jwt.encode(
            {'user_id': user_id, 'expire': expires_date_unix},
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ENCODE_ALGORITHM
        )

    def get_user_id_from_access_token(self, access_token: str) -> int:
        try:
            payload = jwt.decode(
                access_token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ENCODE_ALGORITHM]
            )
        except JWTError:
            raise InvalidTokenException()

        if payload['expire'] < dt.datetime.now(dt.UTC).timestamp():
            raise TokenExpiredException()

        user_id = payload['user_id']
        if not self.user_repo.get_user(user_id):
            raise UserNotFound()

        return user_id

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
