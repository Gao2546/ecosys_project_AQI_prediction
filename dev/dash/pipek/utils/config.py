import os
import flask
import logging

from dotenv import load_dotenv, dotenv_values

logger = logging.getLogger(__name__)

settings = None

import json


def get_settings():
    global settings

    if not settings:
        filename = os.environ.get("PIPEK_SETTINGS", None)

        # if filename is None:
        #     print('This program require NOKKHUM_SETTINGS environment')

        logger.debug(f"setting environment file: {filename}")

        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")

        settings = flask.config.Config(file_path)
        settings.from_object("pipek.default_settings")
        settings.from_envvar("PIPEK_SETTINGS", silent=True)

        load_dotenv()
        config_env = os.environ.get("PIPEK_ENV", ".env")
        settings.update(dotenv_values(config_env))

    return settings
