from typing import Optional , List
import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String , JSON

from . import base


class Output(base.Base):
    __tablename__ = "model"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150),unique=False,nullable=False)
    path: Mapped[str] = mapped_column(String(500),unique=True,nullable=False)
    filename: Mapped[List[str]] = mapped_column(String(500),unique=True,nullable=False)
    results: Mapped[list] = mapped_column(JSON)

    created_date: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now
    )
    updated_date: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now
    )
