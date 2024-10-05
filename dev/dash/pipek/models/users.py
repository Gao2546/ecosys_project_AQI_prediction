from typing import Optional
import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


from . import base


class User(UserMixin,base.Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(150),unique=True,nullable=False)
    email: Mapped[str] = mapped_column(String(150),unique=True,nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String(150),nullable=False)
