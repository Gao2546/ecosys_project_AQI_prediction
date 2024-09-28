import redis


class RedisClient:
    def __init__(self):
        self.client = None

    def init_app(self, app):
        self.client = redis.Redis.from_url(
            app.config.get("REDIS_URL", "redis://localhost:6379")
        )

    def get(self, key):
        return self.client.json().get(key)


redis_client = RedisClient()


def init_redis(app):
    redis_client.init_app(app)
