# -*- coding: UTF-8 -*-
from flask import Blueprint,request,jsonify
from models import *
from redisConn import redis_store,RedisQueue
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
    attackerid=redis_store.hget('attackpack',fr)
    if not attackerid:
        return jsonify({"status":"fail"})
    attack=redis_store.hget('teams',attackerid)
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
    #获取被攻击队伍的信息
    attacked=json.loads(redis_store.hget('teams',flagInfo['teamid']))
    
    connect_queue=RedisQueue('flag_message')
    connect_queue.put(json.dumps({
        'command':'add',
        'score':chal['score'],
        'teamid':attacker['id']
    }))
    connect_queue.put(json.dumps({
        'command':'sub',
        'score':chal['score'],
        'teamid':attacked['id']
    }))
    ttl=redis_store.ttl('flags')
    redis_store.set(fr+flag,1)
    redis_store.expire(fr+flag,ttl)

    instance=json.loads(redis_store.hget('instances',flagInfo['instid']))
    if instance['attack_status']=='stable':
        instance['attack_status']='attacked'
    elif instance['attack_status']=='down':
        instance['attack_status']='d/a'
    redis_store.hset('instances',flagInfo['instid'],json.dumps(instance))
    #写回数据到redis中
    redis_store.rpush('attack',json.dumps({
        'attacker':attacker['id'],
        'attacked':attacked['id'],
        'chal':chal['id'],
        'time':str(datetime.datetime.utcnow())
    }))
    return jsonify({'status':'success'})




