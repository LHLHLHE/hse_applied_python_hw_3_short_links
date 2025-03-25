from pydantic import BaseModel


class UserLoginSchema(BaseModel):
    id: int
    access_token: str


class UserCreateSchema(BaseModel):
    username: str
    password: str
