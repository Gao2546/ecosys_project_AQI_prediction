from typing import Optional
import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String


from . import base


class Image(base.Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String(500))
    filename: Mapped[Optional[str]]
    results: Mapped[Optional[str]] = mapped_column(default="")

    created_date: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now
    )
    updated_date: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now
    )

    status: Mapped[str] = mapped_column(String(10), default="waiting")
