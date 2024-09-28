import asyncio
import datetime
import json
import pathlib


import os

import redis
from rq import Worker, Queue, Connection, SimpleWorker

from pipek import models

import logging

logger = logging.getLogger(__name__)

listen = ["default"]


class IfdashWorker(SimpleWorker):
    def __init__(self, *args, **kwargs):
        settings = kwargs.pop("settings")
        super().__init__(*args, **kwargs)

        models.init_sqlalchemy(settings)


class WorkerServer:
    def __init__(self, settings):
        self.settings = settings

        redis_url = settings.get("REDIS_URL", "redis://localhost:6379")
        self.conn = redis.from_url(redis_url)

    def run(self):
        with Connection(self.conn):
            worker = IfdashWorker(list(map(Queue, listen)), settings=self.settings)
            worker.work()
