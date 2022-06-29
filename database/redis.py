import redis
from settings import settings


redis_conn = redis.Redis.from_url(settings.redis_url)