import asyncio
import dash
import dash_bootstrap_components as dbc

import redis

from .. import models
from . import callbacks
from . import redis_caches


# external_stylesheets = ["/static/node_modules/fomantic-ui-css/semantic.min.css"]
external_stylesheets = [
    dbc.themes.SUPERHERO,
    dbc.icons.BOOTSTRAP,
    dbc.icons.FONT_AWESOME,
]
URL_BASE_PATHNAME = "/dashboard/"


def init_dash(app):
    dash_app = dash.Dash(
        __name__,
        use_pages=True,
        pages_folder="pages",
        url_base_pathname=URL_BASE_PATHNAME,
        suppress_callback_exceptions=True,
        external_stylesheets=external_stylesheets,
        server=app,
    )

    # dash_app.init_app(app)

    redis_caches.init_redis(app)

    if app.config.get("DEBUG", False):
        dash_app.enable_dev_tools(
            dev_tools_ui=True,
            dev_tools_serve_dev_bundles=True,
        )
