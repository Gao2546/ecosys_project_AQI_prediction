from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from . import base
from . import images

from .images import Image

db = SQLAlchemy(model_class=base.Base)
engine = None


def init_db(app):
    print("initial db")

    db.init_app(app)
    with app.app_context():
        db.create_all()


def init_sqlalchemy(settings):
    global engine
    engine = create_engine(settings.get("SQLALCHEMY_DATABASE_URI"), echo=True)


def get_session():
    if engine:
        return Session(engine)
