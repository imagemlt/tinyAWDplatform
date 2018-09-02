from flask_redis import FlaskRedis
redis_store=FlaskRedis()


class RedisQueue(object):
    def __init__(self, name, namespace='queue', **redis_kwargs):
        self.key = "%s:%s" % (namespace, name)

    def qsize(self):
        return redis_store.llen(self.key)

    def put(self, item):
        redis_store.rpush(self.key, item)

    def get_wait(self, timeout=None):
        item = redis_store.blpop(self.key, timeout=timeout)
        return item

    def get_nowait(self):
        item = redis_store.lpop(self.key)
        return item

