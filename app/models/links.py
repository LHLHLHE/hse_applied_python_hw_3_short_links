import datetime as dt
from typing import Optional

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Link(Base):
    __tablename__ = 'links'

    id: Mapped[int] = mapped_column(primary_key=True)
    original_url: Mapped[str]
    short_code: Mapped[str] = mapped_column(unique=True, index=True)
    short_link: Mapped[str]
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC)
    )
    redirect_count: Mapped[int] = mapped_column(default=0)
    last_used_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[dt.datetime]] = mapped_column(DateTime(timezone=True))
    is_expired: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
