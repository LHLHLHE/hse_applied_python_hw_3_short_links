import datetime as dt

from pydantic import (
    BaseModel,
    AnyHttpUrl,
    HttpUrl,
    field_validator
)


class LinkSchema(BaseModel):
    id: int
    original_url: AnyHttpUrl
    short_code: str
    short_link: HttpUrl
    created_at: dt.datetime
    redirect_count: int
    last_used_at: dt.datetime | None = None
    expires_at: dt.datetime | None = None
    is_expired: bool
    user_id: int | None = None

    class Config:
        from_attributes = True


class LinkUpdateSchema(BaseModel):
    original_url: AnyHttpUrl


class LinkCreateSchema(LinkUpdateSchema):
    custom_alias: str | None = None


class CreateLinkParams(BaseModel):
    expires_at: dt.datetime | None = None

    @field_validator("expires_at", mode="before")
    @classmethod
    def validate_expires_at(cls, value) -> dt.datetime | None:
        if value is None:
            return None

        if isinstance(value, dt.datetime):
            value = value.replace(second=0, microsecond=0)
        else:
            try:
                value = dt.datetime.strptime(value, '%Y-%m-%dT%H:%M')
            except ValueError:
                raise ValueError(
                    "Неверный формат даты. Используйте 'YYYY-MM-DDThh:mm', "
                    "например: 2025-03-31T23:45"
                )

        if value.tzinfo is None:
            value = value.replace(tzinfo=dt.UTC)

        if value <= dt.datetime.now(dt.UTC).replace(second=0, microsecond=0):
            raise ValueError('Дата истечения должна быть в будущем')
        return value


class LinkUpdateStatsSchema(BaseModel):
    redirect_count: int
    last_used_at: dt.datetime


class LinkStatsSchema(BaseModel):
    original_url: AnyHttpUrl
    created_at: dt.datetime
    redirect_count: int
    last_used_at: dt.datetime | None

    class Config:
        from_attributes = True
