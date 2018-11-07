# -*- coding: UTF-8 -*-
import redis
#from AWD.models import *
import docker
import json
from config import docker_config
import threading
import uuid
import datetime

redis_store=redis.Redis(host=docker_config['redis_host'],
                        port=docker_config['redis_port'],
                        password=docker_config['redis_password'],
                        db=docker_config['redis_db'])


class DockerManage(object):

    def __init__(self,config):
        self.config=config
        self.instances = []
        self.containers=[]
        self.docker_client=docker.DockerClient(base_url=self.config['baseurl'])
        self.stopped=False

    def build_subnet(self):
        try:
            #subnet_collections=[]
            #chalids=redis_store.hgetall('chals')
            #teamids=redis_store.hgetall('teams')
            print self.config['network_prefix']+'.0.0/16'
            ipam_pool = docker.types.IPAMPool(
                subnet=self.config['network_prefix']+'.0.0/16'
            )
            ipam_config = docker.types.IPAMConfig(
                pool_configs=[ipam_pool]
            )
            self.network=self.docker_client.networks.create(
                                                            self.config['network_name'],
                                                            driver='bridge',
                                                            ipam=ipam_config
                                                            )
            return {'status':'success'}
        except Exception,e:
            return {'status':'fail','reason':str(e)}


    def initialize_containers(self):
        teamids=redis_store.hgetall('teams')
        chalids=redis_store.hgetall('chals')
        chals=[]
        for chalid in chalids:
            chals.append(json.loads(redis_store.hget('chals',chalid)))
        #print chals
        instanceid=0
        err=[]
        for teamid in teamids:
            team=json.loads(redis_store.hget('teams',teamid))
            for chal in chals:
                print chal
                try:
                    if chal['command'] is not None and chal['command'].strip()=='':
                        chal['command']=None
                    container=self.docker_client.containers.create(chal['dockername'],
                                                                   name=self.config['network_name']+'_'+chal['name']+'_team_'+str(teamid),
                                                                   command=chal['command'],
                                                                   detach=True)
                    self.network.connect(container,
                                         ipv4_address=self.config['network_prefix']+'.'+str(teamid)+'.'+str(chal['id']))
                    self.containers.append(container)
                    instance={
                        'name':self.config['network_name']+'_'+chal['name']+'_team_'+str(teamid),
                        'id':instanceid,
                        'chalid':chal['id'],
                        'ip':self.config['network_prefix']+'.'+str(teamid)+'.'+str(chal['id']),
                        'teamid':teamid,
                        'password':str(uuid.uuid4()),
                        'status':container.status
                    }
                    self.instances.append(instance)
                    redis_store.hset('instances',instanceid,json.dumps(instance))
                    team['instances'].append(instanceid)
                except Exception,e:
                    err.append({'teamid':teamid,'chalid':chal['id'],'reason':str(e)})
                instanceid += 1
            redis_store.hset('teams',teamid,json.dumps(team))
        if len(err):

            return {'status':'fail','reason':err}
        return {'status':'success'}

    def start_all(self):
        err=[]
        for instid in range(0,len(self.containers)):
            try:
                self.containers[instid].start()
                instance=json.loads(redis_store.hget('instances',instid))
                self.chpass(instid,instance['password'])
                instance['status']=self.containers[instid].status
                redis_store.hset('instances',instid,json.dumps(instance))
            except Exception,e:
                err.append({'id':instid,'reason':str(e)})
        if len(err):
            return {'status':'fail','reason':err}
        return {'status':'success'}

    def chpass(self,instid,password):
        try:
            instance = json.loads(redis_store.hget('instances', instid))
            self.containers[instid].exec_run("/bin/bash -c 'echo %s:%s|chpasswd'"%(self.config['ssh_user'],password), detach=True)
            instance['password']=password
            redis_store.hset('instances', instid, json.dumps(instance))
        except Exception, e:
            print '[-]%s' % str(e)

    def stop(self,instid):
        try:
            if self.containers[instid].status=='running' or self.containers[instid].status=='paused':
                self.containers[instid].stop()
                instance=json.loads(redis_store.hget('instances',instid))
                instance['status']=self.containers[instid].status
                redis_store.hset('instances',instid,json.dumps(instance))
            return {'status':'success'}
        except Exception,e:
            return {'status':'fail','reason':str(e)}

    def restart(self,instid):
        try:
            self.containers[instid].stop()
            self.containers[instid].remove()
            instance=json.loads(redis_store.hget('instances',instid))
            team=json.loads(redis_store.hget('teams',instance['teamid']))
            chal=json.loads(redis_store.hget('chals',instance['chalid']))
            self.containers[instid] = self.docker_client.containers.create(chal['dockername'],
                                                             name=self.config['network_name'] +'_'+ chal[
                                                                 'name'] + '_team_' + str(team['id']),
                                                             command=chal['command'],
                                                             detach=True)
            self.network.connect(self.containers[instid],
                                 ipv4_address=instance['ip'])
            self.containers[instid].start()
            instance['status']=self.containers[instid].status
            redis_store.hset('instances',instid,json.dumps(instance))
            return {'status':'success'}
        except Exception,e:
            return {'status':'fail','reason':str(e)}

    def pause_all(self):
        err=[]
        for instid in range(0,len(self.containers)):
            try:
                self.containers[instid].pause()
                instance = json.loads(redis_store.hget('instances', instid))
                instance['status'] = self.containers[instid].status
                redis_store.hset('instances', instid, json.dumps(instance))
            except Exception,e:
                err.append({'id':instid,'reason':str(e)})
        if len(err):
            return {'status':'fail','reason':err}
        return {'status':'success'}

    def unpause_all(self):
        err = []
        for instid in range(0, len(self.containers)):
            try:
                self.containers[instid].unpause()
                instance = json.loads(redis_store.hget('instances', instid))
                instance['status'] = self.containers[instid].status
                redis_store.hset('instances', instid, json.dumps(instance))
            except Exception, e:
                err.append({'id': instid, 'reason': str(e)})
        if len(err):
            return {'status': 'fail', 'reason': err}
        return {'status': 'success'}

    def destroy(self):
        for instid in range(0,len(self.containers)):
            try:
                if self.containers[instid].status!='exited':
                    self.containers[instid].stop()
                self.containers[instid].remove()
            except Exception,e:
                print '[-]%s' % str(e)
        try:
            self.network.remove()
            self.stopped=True
        except Exception,e:
            print '[-]%s' % str(e)

    def update_flag(self):
        for instid in range(0,len(self.containers)):
            try:
                instance=json.loads(redis_store.hget('instances',instid))
                chal=json.loads(redis_store.hget('chals',instance['chalid']))
                flag=self.config['flag_prefix']+'{'+str(uuid.uuid4())+'}'
                self.containers[instid].exec_run(chal['flagcommand'].replace('flag{test}',flag),detach=True)
                redis_store.hset('flags',flag,json.dumps({'teamid':instance['teamid'],'chalid':instance['chalid']}))
            except Exception,e:
                print '[-]%s'%str(e)
        redis_store.expire('flags',self.config['expire'])

    def is_stopped(self):
        return self.stopped



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

    docker_manage=DockerManage(docker_config)
    #docker_manage.build_subnet()
    '''
    TODO
    '''
    redis_queue=RedisQueue('docker_message')
    print "[+]redis connection initialized"
    time_begin=datetime.datetime.now()
    while True:
        try:
            data=(redis_queue.get_wait(timeout=10))
            time_end=datetime.datetime.now()
            if (time_end-time_begin).seconds>=docker_config['time_interval']:
                print '[+]time to update flags'
                docker_manage.update_flag()
                time_begin=datetime.datetime.now()
            if not data:
                continue
            info=json.loads(data[1])
            print info
            print info['command']
            if info['command']=='start_all':
                print "[+]building subnet"
                print docker_manage.build_subnet()
                print "[+]init"
                print docker_manage.initialize_containers()
                print "[+]start"
                print docker_manage.start_all()
                redis_store.set(info['mark'],'success')
            elif info['command']=='restart':
                print docker_manage.restart(info['id'])
                redis_store.set(info['mark'],'success')
            elif info['command']=='stop':
                docker_manage.stop(info['id'])
                redis_store.set(info['mark'],'success')
            elif info['command']=='pause':
                pass
                #docker_manage.pause(info['id'])
            elif info['command']=='pause_all':
                docker_manage.pause_all()
                redis_store.set(info['mark'],'success')
            elif info['command']=='unpause_all':
                docker_manage.unpause_all()
                redis_store.set(info['mark'],'success')
            elif info['command']=='destroy':
                docker_manage.destroy()
                redis_store.set(info['mark'],'success')
                break
        except Exception,e:
            print e
            try:
                redis_store.set(info['mark'],str(e))
            except:
                pass
            continue
    if not docker_manage.is_stopped():
        docker_manage.destroy()
    print "[-]ended"
    #redis_store.flushall()
