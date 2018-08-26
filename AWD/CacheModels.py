# -*- coding: UTF-8 -*-
from models import *
from flask_redis import redis

class CacheModel(object):
    def __init__(self,dbmodel,host='localhost',port='6379',db=0):
        self.conn=redis.StrictRedis(host,port,db)
        self.model=dbmodel

    def store(self):
        db.session.add(self.model)
        db.session.commit()
