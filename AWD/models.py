# -*- coding: UTF-8 -*-
from flask_sqlalchemy import SQLAlchemy
import datetime
import uuid

db=SQLAlchemy()

chal_type=('web','pwn')

'''
配置类，表示一些平台相关的配置
'''

class Config(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    config_key=db.Column(db.String(32),unique=True)
    config_value=db.Column(db.Text)

    def __init__(self,key,val):
        self.config_key=key
        self.config_val=val

    def serialize(self):
        return {
            'id':self.id,
            'config_key':self.config_key,
            'config_value':self.config_value
        }

'''
Flag类，表示gamebox的flag
'''
class Flags(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    flag=db.Column(db.String(128),unique=True)
    teamid=db.Column(db.Integer)
    chalid=db.Column(db.Integer)

    def __init__(self,flag,teamid):
        self.flag=flag
        self.teamid=teamid

    def serialize(self):
        return {
            'id':self.id,
            'flag':self.flag,
            'teamid':self.teamid,
            'chalid':self.chalid
        }

'''
Admin类，表示系统管理员
'''
class Admin(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(32),unique=True)
    password=db.Column(db.String(128))

    def __init__(self,name,password):
        self.name=name
        self.password=password

    def serialize(self):
        return {
            'id':self.id,
            'flag':self.flag,
            'teamid':self.teamid,
            'chalid':self.chalid
        }

'''
Teams类，表示所有的队伍
'''
class Teams(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(32),unique=True)
    nickname=db.Column(db.String(32))
    score=db.Column(db.Integer)
    password=db.Column(db.String(128))
    attackid=db.Column(db.String(128),default=str(uuid.uuid4()))
    instances=db.relationship('Instances',backref='team')
    origin_pass=db.relationship('Origin',backref='team')

    def __init__(self,name,password):
        self.name=name
        self.password=password

    def serialize(self):
        return {
            'id':self.id,
            'name':self.name,
            'score':self.score,
            'password':self.password
        }

'''
Attack类，表示一次攻击
'''
class Attack(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    attacker=db.Column(db.Integer)
    defence=db.Column(db.Integer)
    chalid=db.Column(db.Integer)
    time=db.Column(db.DateTime,default=datetime.datetime.utcnow)

    def __init__(self,attacker,defence,chalid,time):
        self.attacker=attacker
        self.defence=defence
        self.chalid=chalid
        self.time=time

    def serialize(self):
        return {
            'id':self.id,
            'attacker':self.attacker,
            'defence':self.defence,
            'chalid':self.chalid,
            'time':str(self.time)
        }
'''
Challenge类，表示每个题目
'''
class Challenges(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(128))
    dockername=db.Column(db.String(128))
    type=db.Column(db.Enum(*chal_type))
    score=db.Column(db.Integer)
    command=db.Column(db.String(128))
    flagcommand=db.Column(db.String(128))
    desc=db.Column(db.String(128))
    instances=db.relationship("Instances",backref='chal')
    hints=db.relationship('Hints',backref='chal')

    def __init__(self,name,dockername,type,score):
        self.name=name
        self.dockername=dockername
        self.type=type
        self.score=score

    def serialize(self):
        return {
            'id':self.id,
            'name':str(self.name),
            'dockername':str(self.dockername)
        }

'''
Instance类，表示每个运行的docker实例
'''
class Instances(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    instancename=db.Column(db.String(128))
    ip=db.Column(db.String(128))
    uid=db.Column(db.Integer,db.ForeignKey('teams.id'))
    chalid=db.Column(db.Integer,db.ForeignKey('challenges.id'))
    ssh_key=db.Column(db.String(128))
    status=db.Column(db.String(10),default='stable')

    def __init__(self,name):
        self.instancename=name

'''
Hint类
'''
class Hints(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    chalid=db.Column(db.Integer,db.ForeignKey('challenges.id'))
    value=db.Column(db.Text)
    time=db.Column(db.DateTime,default=datetime.datetime.utcnow)

    def __init__(self,chal,val):
        self.chalid=chal
        self.value=val


class Origin(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    teamid=db.Column(db.Integer,db.ForeignKey('teams.id'))
    password=db.Column(db.String(64))

if(__name__=='__main__'):
    db.create_all()
