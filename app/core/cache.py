import time

import redis

from app.config import settings
from app.core.logger import logger
from app.middlewares.context_capture import get_redis_log_context


def get_redis(db = 0):
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=db,
        socket_timeout=5
    )

class RedisClient:
    environment = 'local'
    def __init__(self, db=0):
        self.cache = get_redis(db=db)
        self.environment = settings.APP_ENV

    def prefix(self):
        return f'{self.environment}:'

    def set(self, key, value, ttl_in_seconds=None, name=None):
        start_time = time.time()
        key = f'{self.prefix()}{key}'
        debug_loggable = {
            "operation": "set",
            "key": key,
            "expire": ttl_in_seconds,
            "duration": 0,
        }
        try:
            self.cache.set(key, value, ex=ttl_in_seconds)
            return True
        except Exception as e:
            logger.debug(f'Error setting cache: {str(e)}')
            return False
        finally:
            log_context = get_redis_log_context()
            debug_loggable["duration"] = time.time() - start_time
            log_context.append(debug_loggable)

    def get(self, key, name=None):
        start_time = time.time()
        key = f'{self.prefix()}{key}'
        debug_loggable = {
            "operation": "get",
            "key": key,
            "hit": False,
            "duration": 0,
        }

        try:
            value = self.cache.get(key)
            if value:
                debug_loggable["hit"] = True
            return None, value
        except Exception as e:
            logger.debug(f'Error getting cache: {str(e)}')
            return e, None
        finally:
            log_context = get_redis_log_context()
            debug_loggable["duration"] = time.time() - start_time
            log_context.append(debug_loggable)

    def mget(self, keys, name=None):
        start_time = time.time()
        keys = [f'{self.prefix()}{key}' for key in keys]
        debug_loggable = {
            "operation": "mget",
            "hit": {k: False for k in keys },
            "duration": 0,
        }
        try:
            values = self.cache.mget(keys)
            debug_loggable["hit"] = {k: v is not None for k, v in zip(keys, values)}
            return None, values
        except Exception as e:
            logger.debug(f'Error in mget: {str(e)}')
            return e, [None for _ in keys]
        finally:
            log_context = get_redis_log_context()
            debug_loggable["duration"] = time.time() - start_time
            log_context.append(debug_loggable)

    def delete(self, key):
        key = f'{self.prefix()}{key}'
        self.cache.delete(key)

    def flush(self):
        self.cache.flushdb()

    def pipeline(self, callback):
        pipe = self.cache.pipeline()
        callback(pipe)
        return pipe.execute()

    def hget_using_pipeline(self, keys):
        pipe = self.cache.pipeline()
        for key in keys:
            key = f'{self.prefix()}{key}'
            pipe.hgetall(key)
        return pipe.execute()

    def hdel_using_pipeline(self, keys):
        pipe = self.cache.pipeline()
        for key in keys:
            key = f'{self.prefix()}{key}'
            pipe.delete(key)
        pipe.execute()

    def delete_using_pipeline(self, keys):
        start_time = time.time()
        debug_loggable = {
            "operation": "delete",
            "keys": keys,
            "prefix": self.prefix(),
            "deleted": 0,
            "duration": 0,
        }
        with self.cache.pipeline() as pipe:
            count = 0
            deleted = 0
            for key in keys:
                key = f'{self.prefix()}{key}'
                pipe.delete(key)
                count += 1
                if count % 1000 == 0:
                    result = pipe.execute(raise_on_error=False)
                    deleted += result.count(1)
            if count % 1000 != 0:
                result = pipe.execute(raise_on_error=False)
                deleted += result.count(1)
            log_context = get_redis_log_context()
            debug_loggable["deleted"] = deleted
            debug_loggable["duration"] = time.time() - start_time
            log_context.append(debug_loggable)

        return deleted