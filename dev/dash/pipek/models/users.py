from typing import Optional
import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String , Integer


from . import base


class User(base.Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150),unique=True,nullable=False)
    email: Mapped[str] = mapped_column(String(150),unique=True,nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String(150),nullable=False)
    status: Mapped[int] = mapped_column(Integer,nullable=False,default=0)
