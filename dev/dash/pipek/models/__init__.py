from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from . import base
from . import images
from . import users

from .users import User

from .images import Image

db = SQLAlchemy(model_class=base.Base)
engine = None


def init_db(app):
    print("initial db")
    app.config["SECRET_KEY"] = "This is secret key"
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://coe:CoEpasswd@proj-postgresql-1:5432/schematics_appdb"

    db.init_app(app)
    with app.app_context():
        db.create_all()


def init_sqlalchemy(settings):
    # global engine
    # engine = create_engine("postgresql://coe:CoEpasswd@localhost:5432/schematics_appdb",\
    #           echo=True)
    print('init engin')


def get_session():
    if engine:
        return Session(engine)
