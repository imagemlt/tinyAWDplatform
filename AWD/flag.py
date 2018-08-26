# -*- coding: UTF-8 -*-
from flask import Blueprint,request,jsonify
from models import *
from redisConn import redis_store
import json

flag=Blueprint('flag',__name__)

'''
攻击接口
'''
@flag.route('/flag',methods=['GET'])
def treatflag():
    flag=request.args.get('flag')
    fr=request.args.get('from')
    #flag查询结果
    result=redis_store.hget('flags',flag)
    #攻击方查询结果
    attack=redis_store.hget('teams',fr)
    if not result or not attack:
        return jsonify({"status":"fail"})
    if redis_store.get(fr+flag):
        return jsonify({"status":"fail"})
    #获取flag信息与攻击方信息
    flagInfo=json.loads(result)
    attacker=json.loads(attack)
    if flagInfo['teamid']==attacker['id']:
        return jsonify({"status":"fail"})
    #获取题目信息
    chal=json.loads(redis_store.hget('chals',flagInfo['chalid']))
    print chal
    #获取被攻击队伍的信息
    attacked=json.loads(redis_store.hget('teams',flagInfo['teamid']))
    print attacked,attacker
    #攻击方加分，被攻击方减分
    attacker['score']=attacker['score']+chal['score']
    attacked['score']=attacked['score']-chal['score']
    print attacked,attacker
    ttl=redis_store.ttl('flags')
    redis_store.set(fr+flag,1)
    redis_store.expire(fr+flag,ttl)
    #写回数据到redis中
    redis_store.hset('teams',attacker['id'],json.dumps(attacker))
    redis_store.hset('teams',attacked['id'],json.dumps(attacked))
    redis_store.rpush('attack',json.dumps({'attacker':attacker['id'],'attacked':attacked['id'],'chal':chal['id'],'time':str(datetime.datetime.utcnow())}))
    return jsonify({'status':'success'})




