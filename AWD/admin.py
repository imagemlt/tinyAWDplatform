# -*- coding: UTF-8 -*-
import hashlib
from models import *
import functools
from redisConn import redis_store,RedisQueue
import json
import uuid
from flask import Blueprint,session,abort,render_template,redirect,jsonify,request

admin=Blueprint('admin',__name__)



def is_admin(func):
    @functools.wraps(func)
    def wrapper(*args,**kargs):
        if not session.has_key('is_admin') or not session['is_admin']:
            return redirect('/admin/index.html/#login')
        return func(*args,**kargs)
    return wrapper

def load_to_redis():
    chals=Challenges.query.all()
    teams=db.session.query(Teams).join(Origin).all()
    chals_dict={}
    teams_dict={}
    for chal in chals:
        chals_dict[chal.id]=json.dumps({
            'id': chal.id,
            'name': chal.name,
            'dockername': chal.dockername,
            'type': chal.type,
            'score': chal.score,
            'command': chal.command,
            'flagcommand': chal.flagcommand,
            'desc': chal.desc
        })
    if len(chals_dict):
        redis_store.hmset('chals',chals_dict)
    for team in teams:
        teams_dict[team.id]=json.dumps({
            'id': team.id,
            'name': team.name,
            'nickname': team.nickname,
            'score': team.score,
            'password': team.origin_pass[0].password,
            'attackid':team.attackid,
            'instances': []
        })
    if not redis_store.hget('attackpack',team.attackid):
        redis_store.hset('attackpack',team.attackid,team.id)
    if len(teams_dict):
        redis_store.hmset('teams',teams_dict)

@admin.route('/admin')
def admin_index():
    return render_template('/admin/index.html')

@admin.route('/admin/login',methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        uname=request.form.get('username')
        pwd=request.form.get('password')
        md5=hashlib.md5()
        md5.update(pwd)
        pwd=md5.hexdigest()
        user=Admin.query.filter(Admin.name==uname).first()
        if not user or user.password !=pwd:
            return jsonify({
                'code':403,
                'msg':'登陆失败',
                'type':'fail'
            })
        session['is_admin']=True
        session['username']=user.name
        session['userid']=user.id
        return jsonify({
            'code':200,
            'msg':'登陆成功',
            'type':'success',
            'user':{
                'id':user.id,
                'name':user.name,
                'avatar':'https://susers.github.io/images/logo.jpg',
                'username':user.name
            }
        })
    else:
        return redirect('/admin')

@admin.route('/admin/add',methods=['POST'])
@is_admin
def admin_add():
        uname=request.form.get('name')
        pwd=request.form.get('password')
        user=Admin.query.filter(Admin.name==uname).first()
        if user:
            return jsonify({
                'code':500,
                'msg': '添加admin失败：用户名已存在',
                'type': 'fail'
            })
        #pwd_confirm=request.form.get('pwd_confirm')
        #if pwd_confirm != pwd:
        #    return redirect('/admin/add?status=notsame')
        md5=hashlib.md5()
        md5.update(pwd)
        pwd=md5.hexdigest()
        user=Admin(uname,pwd)
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'code':200,
            'msg':'添加成功',
            'type':'success'
        })


@admin.route('/admin/list',methods=['GET'])
@is_admin
def admin_list():
    total = db.session.query(db.func.count(Admin.id)).scalar()
    if request.args.has_key('page'):
        page = int(request.args['page'])
        admins=Admin.query.limit(20).offset((page - 1) * 20).all()
    else:
        admins = Admin.query.all()
    ans = []
    for admin in admins:
        ans.append({
            'id': admin.id,
            'name':admin.name
        })
    return jsonify({
        'total': total,
        'admins': ans
    })

@admin.route('/admin/edit',methods=['POST'])
@is_admin
def admin_edit():
    admin = Admin.query.filter(Admin.id == request.form.get('id')).first()
    if not admin:
        return abort(404)
    admin2 = Admin.query.filter(Admin.name == request.form.get('name')).first()
    if admin2 and admin2.id != admin.id:
        print admin2.id
        print request.form.get('id')
        return jsonify({
            'code':500,
            'msg': '编辑失败:用户名已存在',
            'type': 'fail'
        })
    md5=hashlib.md5()
    md5.update(request.form.get('password'))
    pwd=md5.hexdigest()
    admin.name=request.form.get('name')
    admin.password=pwd
    db.session.commit()
    return jsonify({
        'code':200,
        'msg':'编辑成功',
        'type':"success"
    })

@admin.route('/admin/remove',methods=['POST'])
@is_admin
def delete_admin():
    id=request.form.get('id')
    admin=Admin.query.filter(Admin.id==id).first()
    if not admin:
        return abort(404)
    db.session.delete(admin)
    db.session.commit()
    return jsonify({
        'code':200,
        'msg':'删除成功',
        'type':'fail'
    })

@admin.route('/admin/chals/add',methods=['POST'])
@is_admin
def add_chal():
    chal=Challenges.query.filter(Challenges.name==request.form.get('name')).first()
    if chal:
        return jsonify({
            'code':500,
            'msg':'添加chal失败：用户名已存在',
            'type':'fail'
        })
    chalname=request.form.get('name')
    chaltype=request.form.get('type')
    dockername=request.form.get('dockername')
    score=request.form.get('score')
    Chal=Challenges(chalname,dockername,chaltype,score)
    Chal.command=request.form.get('command')
    Chal.flagcommand=request.form.get('flagcommand')
    Chal.desc=request.form.get('desc')
    db.session.add(Chal)
    db.session.commit()
    print Chal.dockername
    redis_store.hset('chals',Chal.id,json.dumps({
        'id': Chal.id,
        'name': Chal.name,
        'dockername': Chal.dockername,
        'type': Chal.type,
        'score': Chal.score,
        'command': Chal.command,
        'flagcommand': Chal.flagcommand,
        'desc': Chal.desc
    }))
    return jsonify({
        'code':200,
        'msg':'添加成功',
        'type':'success'
    })


@admin.route('/admin/chals/edit',methods=['POST'])
@is_admin
def edit_chal():
    chal=Challenges.query.filter(Challenges.id==request.form['id']).first()
    if not chal:
        return abort(404)
    chal2=Challenges.query.filter(Challenges.name==request.form.get('name')).first()
    if chal2 and chal2.id != chal.id:
        return jsonify({
            'code':500,
            'msg':'编辑失败:chal已存在',
            'type':'fail'
        })
    chalname=request.form.get('name')
    chaltype=request.form.get('type')
    dockername=request.form.get('dockername')
    score=request.form.get('score')
    chal.name=chalname
    chal.type=chaltype
    chal.dockername=dockername
    chal.score=score
    chal.command=request.form.get('command')
    chal.flagcommand=request.form.get('flagcommand')
    chal.desc=request.form.get('desc')
    db.session.commit()
    redis_store.hset('chals',chal.id,json.dumps({
        'id':chal.id,
        'name':chal.name,
        'dockername':chal.dockername,
        'type':chal.type,
        'score':chal.score,
        'command':chal.command,
        'flagcommand':chal.flagcommand,
        'desc':chal.desc
    }))
    return jsonify({
        'code':200,
        'msg':'编辑成功',
        'type':'success'
    })




@admin.route('/admin/chals/remove',methods=['POST'])
@is_admin
def delete_chal():
    chalid=request.form.get('id')
    chal=Challenges.query.filter(Challenges.id==chalid).first()
    if not chal:
        return abort(404)
    db.session.delete(chal)
    db.session.commit()
    return jsonify({
        'code':200,
        'msg':'删除成功',
        'type':'fail'
    })

@admin.route('/admin/chals/batchremove',methods=['POST'])
@is_admin
def batch_delete_chal():
    chalids=[int(x) for x in request.form.get('ids').split(',')]
    chal=Challenges.query.filter(Challenges.id._in(chalids)).first()
    if not chal:
        return abort(404)
    db.session.delete(chal)
    db.session.commit()
    redis_store.hdel('chals',chal.id)
    return jsonify({
        'code':'200',
        'msg':'删除成功',
        'type':'success'
    })


@admin.route('/admin/chals',methods=['GET'])
@is_admin
def chals():
    ans=[]
    chals_in_redis=redis_store.hgetall('chals')
    if not chals_in_redis:
        total=db.session.query(db.func.count(Challenges.id)).scalar()
        if request.args.has_key('page'):
            page=int(request.args['page'])
            chals=Challenges.query.limit(20).offset((page-1)*20).all()
        else:
            chals=Challenges.query.all()
        result_json={}
        for chal in chals:
            chal_json={
                'id':chal.id,
                'name':chal.name,
                'dockername':chal.dockername,
                'type':chal.type,
                'score':chal.score,
                'command':chal.command,
                'flagcommand':chal.flagcommand,
                'desc':chal.desc
            }
            ans.append(chal_json)
            result_json[chal.id]=json.dumps(chal_json)
        #print len(result_json)
        if len(result_json):
            redis_store.hmset('chals',result_json)
    else:
        total=len(chals_in_redis)
        if request.args.has_key('page'):
            page=int(request.args['page'])
            has_page=True
        else:
            has_page=False
        counter=0
        for chalid in chals_in_redis:
            print chalid
            if has_page and counter<(page-1)*20:
                counter+=1
                continue
            ans.append(json.loads(chals_in_redis[chalid]))
            if has_page and len(ans)==20:
                break
    return jsonify({
        'total':total,
        'chals':ans
    })


@admin.route('/admin/inst/<int:chalid>',methods=['GET'])
@is_admin
def get_instances(chalid):
    instances=redis_store.hgetall('instances')
    ans=[]
    for inst in instances:
        instance=json.loads(instances[inst])
        if instance['chalid']==chalid:
            ans.append(instance)
    return jsonify(ans)


@admin.route('/admin/instances',methods=['GET'])
@is_admin
def get_all_instances():
    page=int(request.args['page'])
    instances=redis_store.hgetall('instances')
    ans=[]
    counter=0
    if(len(instances)==0):
        load_to_redis()
    for inst in instances:
        if counter<(page-1)*20:
            counter+=1
            continue
        inst=json.loads(instances[inst])
        chal=json.loads(redis_store.hget('chals',inst['chalid']))
        team=json.loads(redis_store.hget('teams',inst['teamid']))
        ans.append({
            'id':inst['id'],
            'name': inst['name'],
            'teamname':team['nickname'],
            'chalname':chal['name'],
            'ip':inst['ip'],
            'status':inst['status'],
            'password':inst['password']
        })
        if len(ans)==20:
            break
    return jsonify({
        'total':len(instances),
        'instances':ans
    })

@admin.route('/admin/instances/restart',methods=['POST'])
@is_admin
def inst_restart():
    instid=request.form['id']
    inst=redis_store.hget('instances',instid)
    if not inst:
        return abort(404)
    inst=json.loads(inst)
    connect_queue=RedisQueue('docker_message')
    mark=str(uuid.uuid4())
    connect_queue.put(json.dumps({'command':'restart','id':inst['id'],'mark':mark}))
    if not session.has_key('messids'):
        session['messids']=[]
    print mark
    messids=session['messids']
    messids.append(mark)
    session['messids']=messids
    return jsonify({
        'code':200,
        'msg':'重启指令已发送',
        'id':mark
    })

@admin.route('/admin/instances/chpass',methods=['POST'])
@is_admin
def inst_chpass():
    instid=request.form['id']
    inst=json.loads(redis_store.hget('instances',instid))
    if not inst:
        return abort(404)
    connect_queue=RedisQueue('docker_message')
    mark=str(uuid.uuid1())
    connect_queue.put(json.dumps({'command':'chpass','id':inst['id'],'mark':mark}))
    if not session.has_key('messids'):
        session['messids']=[]
    messids=session['messids']
    messids.append(mark)
    session['messids']=messids
    return jsonify({
        'code':200,
        'msg':'更改密码指令已发送',
        'id':mark
    })


@admin.route('/admin/instances/status')
@is_admin
def inst_restart_status():
    messid=request.args['id']
    ids=session['messids']
    print ids
    if messid not in ids:
        return abort(403)
    data=(redis_store.get(messid))
    if data:
        if data=='success':
            return jsonify({
                'code':200,
                'msg':True,
                'status':'success'
            })
        else:
            return jsonify({
                'code':200,
                'msg':True,
                'status':data
            })
    else:
        return jsonify({
            'code':200,
            'msg':False
        })

@admin.route('/admin/startall',methods=['POST'])
@is_admin
def start():
    connect_queue=RedisQueue('docker_message')
    uid=str(uuid.uuid1())
    connect_queue.put(json.dumps({'command':'start_all','mark':uid}))
    if not session.has_key('messids'):
        session['messids']=[]
    messids=session['messids']
    messids.append(uid)
    session['messids']=messids
    return jsonify({'code':'200','msg':'指令已发送','id':uid})

@admin.route('/admin/pauseall',methods=['POST'])
@is_admin
def pause_all():
    connect_queue=RedisQueue('docker_message')
    uid=str(uuid.uuid1())
    connect_queue.put(json.dumps({'command':'pause_all','mark':uid}))
    if not session.has_key('messids'):
        session['messids']=[]
    messids=session['messids']
    messids.append(uid)
    session['messids']=messids
    return jsonify({'code':'200','msg':'指令已发送','id':uid})

@admin.route('/admin/unpauseall',methods=['POST'])
@is_admin
def unpause_all():
    connect_queue = RedisQueue('docker_message')
    uid = str(uuid.uuid1())
    connect_queue.put(json.dumps({'command': 'unpause_all', 'mark': uid}))
    if not session.has_key('messids'):
        session['messids'] = []
    messids = session['messids']
    messids.append(uid)
    session['messids'] = messids
    return jsonify({'code': '200', 'msg': '指令已发送', 'id': uid})

@admin.route('/admin/destroy',methods=['POST'])
@is_admin
def endup_context():
    connect_queue = RedisQueue('docker_message')
    uid = str(uuid.uuid1())
    connect_queue.put(json.dumps({'command': 'destroy', 'mark': uid}))
    if not session.has_key('messids'):
        session['messids'] = []
    messids = session['messids']
    messids.append(uid)
    session['messids'] = messids
    return jsonify({'code': '200', 'msg': '指令已发送', 'id': uid})

@admin.route('/admin/teams',methods=['GET'])
@is_admin
def getteams():
    ans = []
    result_in_json={}
    teams_in_redis=redis_store.hgetall('teams')
    if not teams_in_redis:
        total = db.session.query(db.func.count(Teams.id)).scalar()
        if request.args.has_key('page'):
            page=int(request.args['page'])
            teams=db.session.query(Teams).join(Origin).limit(20).offset((page-1)*20).all()
        else:
            teams=db.session.query(Teams).join(Origin).all()
        for team in teams:
            print len(team.origin_pass)
            json_team={
                'id':team.id,
                'name':team.name,
                'nickname':team.nickname,
                'score':team.score,
                'password':team.origin_pass[0].password,
                'attackid':team.attackid,
                'instances':[]
            }
            ans.append(json_team)
            result_in_json[team.id]=json.dumps(json_team)
        if len(result_in_json):
            redis_store.hmset('teams',result_in_json)
    else:
        total=len(teams_in_redis)
        if request.args.has_key('page'):
            page=int(request.args['page'])
            has_page=True
        else:
            has_page=False
        counter=0
        for teamid in teams_in_redis:
            if has_page and counter < (page - 1) * 20:
                counter += 1
                continue
            team = json.loads(teams_in_redis[teamid])
            ans.append({
                'id':team['id'],
                'name':team['name'],
                'nickname':team['nickname'],
                'score':team['score'],
                'password':team['password']
            })
            if has_page and len(ans) == 20:
                break
    return jsonify({
        'total':total,
        'teams':ans
    })


@admin.route('/admin/teams/remove',methods=['POST'])
@is_admin
def remove_team():
    id=int(request.form['id'])
    team=Teams.query.filter(Teams.id==id).first()
    if not team:
        abort(404)
    db.session.delete(team)
    db.session.commit()
    if redis_store.hget('teams',request.form['id']):
        redis_store.hdel('teams',request.form['id'])
    return jsonify({
        'message':'删除成功',
        'type':'success'
    })

@admin.route('/admin/teams/batchremove',methods=['GET'])
@is_admin
def remove_team_batch():
    ids=[int(x) for x in request.args('id').split(',')]
    db.session.query(Teams).filter(Teams.id.in_(ids)).delete()
    db.session.commit()
    for id in ids:
        redis_store.hdel('teams',id)
    return jsonify({
        'message':'删除成功',
        'type':'success'
    })


@admin.route('/admin/teams/add',methods=['POST'])
@is_admin
def add_team():
    teamtest=Teams.query.filter(Teams.name==request.form['name']).first()
    if teamtest:
        return jsonify({
            'code':500,
            'msg':"添加失败：用户已存在",
            'type':"fail"
        })
    md5 = hashlib.md5()
    md5.update(request.form['password'])
    pwd = md5.hexdigest()
    team=Teams(request.form['name'],pwd)
    team.nickname=request.form['nickname']
    team.score=10000
    team.attackid=str(uuid.uuid4())
    db.session.add(team)
    db.session.commit()
    origin_pass=Origin()
    origin_pass.password=request.form['password']
    origin_pass.teamid=team.id
    db.session.add(origin_pass)
    db.session.commit()
    redis_store.hset('teams',team.id,json.dumps({
        'id':team.id,
        'name':team.name,
        'nickname':team.nickname,
        'password':origin_pass.password,
        'score':team.score,
        'instances':[],
        'attackid':team.attackid
    }))
    redis_store.hset('attackpack',team.attackid,team.id)
    return jsonify({
        'code':200, 
        'msg':"添加成功",
        'type':"success"
    })




@admin.route('/admin/teams/edit',methods=['POST'])
@is_admin
def changeteam():
    id=request.form['id']
    team=Teams.query.join(Origin).filter(Teams.id==id).first()
    if not team:
        abort(404)
    team2=Teams.query.filter(Teams.name==request.form['name']).first()
    if team2 and team2.id!=team.id:
        return jsonify({
            'code':500,
            'msg':'添加失败：team已存在',
            'type':'fail'
        })
    team_in_redis=json.loads(redis_store.hget('teams',team.id))
    team.name=request.form['name']
    md5=hashlib.md5()
    md5.update(request.form['password'])
    pwd=md5.hexdigest()
    team.password=pwd
    team.score=team_in_redis['score']
    origin_pass=team.origin_pass[0]
    origin_pass.password=request.form['password']
    team.nickname=request.form['nickname']
    db.session.commit()
    redis_store.hset('teams', team.id, json.dumps({
        'id': team.id,
        'name': team.name,
        'nickname': team.nickname,
        'password': origin_pass.password,
        'score': team_in_redis['score'],
        'attackid':team_in_redis['attackid'],
        'instances':team_in_redis['instances']
    }))
    return jsonify({
        'code':200,
        'msg':'更改成功',
        'type':'success'
    })


@admin.route('/admin/logout',methods=['POST'])
@is_admin
def team_logout():
    session.clear()
    return jsonify({
        'code':200,
        'msg':'已注销登录'
    })
