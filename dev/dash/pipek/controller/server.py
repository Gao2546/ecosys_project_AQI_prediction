import asyncio
from dotenv import dotenv_values

import datetime
import json
import pathlib
import logging
import threading
import queue
import time

logger = logging.getLogger(__name__)


from pipek import models
import json


class ControllerServer:
    def __init__(self, settings: dict = dict()):
        self.settings = settings

    async def get_config(self):
        self.settings = dotenv_values(".env")
        for k in self.settings:
            if self.settings[k].strip()[0] in ["[", "{"]:
                self.settings[k] = json.loads(self.settings[k])

    async def initial(self):
        if not self.settings:
            await self.get_config()

    async def interval(self):
        self.running = True
        while self.running:
            print(datetime.datetime.now(), "controller sleep 1s")
            await asyncio.sleep(1)

    async def stop(self):
        self.running = False

    def run(self):
        asyncio.run(self.initial())
        asyncio.run(self.interval())
