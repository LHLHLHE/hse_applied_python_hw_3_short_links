from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = 'postgres'
    POSTGRES_DB: str = 'links'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DRIVER: str = 'postgresql+asyncpg'

    JWT_SECRET_KEY: str ='very_secret_key'
    JWT_ENCODE_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SHORT_CODE_LENGTH: int = 8

    REDIS_URL: str = 'redis://127.0.0.1:6379/0'

    UNUSED_LINKS_TTL_DAYS: int = 30

    @property
    def db_url(self):
        return (
            f'{self.POSTGRES_DRIVER}://{self.POSTGRES_USER}:'
            f'{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:'
            f'{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )


settings = Settings()
