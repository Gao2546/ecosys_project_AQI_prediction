from flask import redirect, url_for, request, session, render_template
from flask_login import current_user, LoginManager, login_url
from werkzeug.exceptions import Forbidden
from . import models


from functools import wraps

login_manager = LoginManager()


def init_acl(app):
    login_manager.init_app(app)
    # principals.init_app(app)

    @app.errorhandler(401)
    def page_not_found(e):
        return unauthorized_callback()

    @app.errorhandler(403)
    def no_permission(e):
        return render_template("error_handler/403.html"), 403


def role_and_division_required(*role_division):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if hasattr(current_user, "division"):
                for role, division in role_division:
                    if role in current_user.roles and division == current_user.division:
                        return func(*args, **kwargs)
            raise Forbidden()

        return wrapped

    return wrapper


def division_required(*divisions):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if hasattr(current_user, "division"):
                for division in divisions:
                    if division == current_user.division:
                        return func(*args, **kwargs)
            raise Forbidden()

        return wrapped

    return wrapper


def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            for role in roles:
                if role in current_user.roles:
                    return func(*args, **kwargs)
            raise Forbidden()

        return wrapped

    return wrapper


@login_manager.user_loader
def load_user(user_id):
    me = session.get("me")
    user = models.users.User(me)
    return user


@login_manager.unauthorized_handler
def unauthorized_callback():
    if request.method == "GET":
        response = redirect("accounts/login")
        return response

    return redirect("accounts/login")
