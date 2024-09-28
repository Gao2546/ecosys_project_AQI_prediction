import os
from dash import DiskcacheManager, CeleryManager

background_callback_manager = None
if "CACHE_REDIS_URL_X" in os.environ:
    # Use Redis & Celery if CACHE_REDIS_URL set as an env variable
    from celery import Celery

    celery_app = Celery(
        __name__,
        broker=os.environ["CACHE_REDIS_URL"],
        backend=os.environ["CACHE_REDIS_URL"],
    )
    background_callback_manager = CeleryManager(celery_app)

else:
    # Diskcache for non-production apps when developing locally
    import diskcache

    cache = diskcache.Cache("./cache")
    background_callback_manager = DiskcacheManager(cache)
