# -*- coding: UTF-8 -*-
import redis
#from AWD.models import *
#import docker
import json
from config import docker_config
import threading
import uuid
import datetime

redis_store=redis.Redis(host=docker_config['redis_host'],
                        port=docker_config['redis_port'],
                        password=docker_config['redis_password'],
                        db=docker_config['redis_db'])


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


if __name__=='__main__':

    #docker_manage=DockerManage(docker_config)
    #docker_manage.build_subnet()
    '''
    TODO
    '''
    redis_queue=RedisQueue('flag_message')
    print "[+]redis connection initialized"
    while True:
        try:
            data=(redis_queue.get_wait(timeout=10))
            if not data:
                continue
            info=json.loads(data[1])
            print info
            print info['command']
            if info['command']=='add':
                print "[+]add score %d to team %d"%(info['score'],info['teamid'])
                team=json.loads(redis_store.hget('teams',info['teamid']))
                team['score']+=info['score']
                redis_store.hset('teams',info['teamid'],json.dumps(team))
            elif info['command']=='sub':
                print "[+]sub score %d to team %d"%(info['score'],info['teamid'])
                team=json.loads(redis_store.hget('teams',info['teamid']))
                team['score']-=info['score']
                redis_store.hset('teams',info['teamid'],json.dumps(team))
            elif info['command']=='exit':
                print '[-]close chal'
                break
        except Exception,e:
            print e
            try:
                print str(e)
            except:
                pass
            continue
    print '[-]chal ended'
    #redis_store.flushall()
