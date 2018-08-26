# -*- coding: UTF-8 -*-
import hashlib
import json
from models import *
from redisConn import redis_store
import functools
from flask import Blueprint,session,abort,render_template,redirect,jsonify,request

teams=Blueprint('teams',__name__)

def login_required(func):
    @functools.wraps(func)
    def wrapper(*args,**kargs):
        if not session.has_key('login') or not session['login']:
            return abort(403)
        return func(*args,**kargs)
    return wrapper

@teams.route('/')
def index():
    return render_template('teams/index.html')

@teams.route('/login',methods=['POST','GET'])
def team_login():
    if request.method=='POST':
        team=Teams.query.filter(Teams.name==request.form.get('username')).first()
        if not team:
            return jsonify({
                'code':403,
                'msg':'用户不存在'
            })
        md5=hashlib.md5()
        md5.update(request.form.get('password'))
        pwd=md5.hexdigest()
        if pwd!=team.password:
            return jsonify({
                'code':403,
                'msg':'密码错误'
            })

        session['login']=True
        session['user']={
            'id':team.id,
            'name':team.name,
            'nickname':team.nickname
        }
        return jsonify({
            'code':200,
            'user':{
                'id':team.id,
                'name':team.name,
                'nickname':team.nickname
            }
        })
    else:
        return render_template('/teams/index.html')


@teams.route('/team/info')
def team_info():
    team=json.loads(redis_store.hget('teams',session['user']['id']))
    if not team:
        abort(404)
    ans={'id':team['id'],'name':team['name'],'nickname':team['nickname'],'score':team['score']}
    return jsonify({
        'user':ans
    })


@login_required
@teams.route('/team/edit',methods=['POST'])
def team_edit():
    team=Teams.query.filter(Teams.id==session['user']['id']).first()
    if not team:
        abort(403)
    md5=hashlib.md5()
    md5.update(request.form.get('old_password'))
    pwd=md5.hexdigest()
    if team.password!=pwd:
        return jsonify({
            'code':403,
            'msg':'密码错误'
        })
    md5=hashlib.md5()
    md5.update(request.form.get('password'))
    pwd=md5.hexdigest()
    team.name=request.form.get('name')
    team.nickname=request.form.get('nickname')
    team.password=pwd
    db.session.commit()
    team_in_redis=json.loads(redis_store.hget('teams',team.id))
    team_in_redis['name']=team.name
    team_in_redis['nickname']=team.nickname
    redis_store.hset('teams',team.id,json.dumps(team_in_redis))
    session['user']['name']=team.name
    session['user']['nickname']=team.nickname
    return jsonify({
        'code':200,
        'msg':'更改成功'
    })


@login_required
@teams.route('/status')
def team_status():
    teamid=session['user']['id']
    team=json.loads(redis_store.hget('teams',id))
    running_instances=[]
    for instance in team['instances']:
        running_instances.append(json.loads(redis_store.hget('instances',instance)))
    team['instances']=running_instances
    return jsonify(team)

'''
@login_required
@teams.route('/profile')
def team_profile():
    teamid=session['id']
    team=json.loads(redis_store.hget('teams',id))
    if request.method=='GET':
        return render_template('team_profile.html',team=team)
    else:
        team_model=Teams.query.filter(Teams.id==id).first()
        team_model.nickname=request.form['nickname']
        if request.form['password']!=request.form['password_twice']:
            return redirect('/profile?error=notsame')
        team_model.password=request.form['password']
        db.session.commit()
        team['nickname']=request.form['nickname']
        team['score']
        redis_store.hput('teams',id,json.dumps(team))
        return redirect('/profile?status=success')
'''


@teams.route('/team/list')
def team_list():
    ans = []
    result_in_json = {}
    teams_in_redis = redis_store.hgetall('teams')
    if not teams_in_redis:
        total = db.session.query(db.func.count(Teams.id)).scalar()
        if request.args.has_key('page'):
            page = int(request.args['page'])
            teams = db.session.query(Teams).join(Origin).limit(20).offset((page - 1) * 20).all()
        else:
            teams = db.session.query(Teams).join(Origin).all()
        for team in teams:
            print len(team.origin_pass)
            json_team = {
                'id': team.id,
                'name': team.name,
                'nickname': team.nickname,
                'score': team.score,
                'password': team.origin_pass[0].password,
                'instances':[]
            }
            ans.append(json_team)
            result_in_json[team.id] = json.dumps(json_team)
        redis_store.hmset('teams', result_in_json)
    else:
        total = len(teams_in_redis)
        if request.args.has_key('page') and request.args['page'] !='':
            page = int(request.args['page'])
            has_page = True
        else:
            has_page = False
        counter = 0
        for teamid in teams_in_redis:
            if has_page and counter < (page - 1) * 20:
                counter += 1
                continue
            team = json.loads(teams_in_redis[teamid])
            ans.append({
                'id': team['id'],
                'name': team['name'],
                'nickname': team['nickname'],
                'score': team['score'],
                'password': team['password']
            })
            if has_page and len(ans) == 20:
                break
    return jsonify({
        'total': total,
        'users': ans
    })



@login_required
@teams.route('/team/instances')
def team_instances():
    teamid=session['user']['id']
    team=json.loads(redis_store.hget('teams',teamid))
    instances=[]
    for instance in team['instances']:
        inst=json.loads(redis_store.hget('instances',instance))
        chal = json.loads(redis_store.hget('chals', inst['chalid']))
        team = json.loads(redis_store.hget('teams', inst['teamid']))
        instances.append({
            'id': inst['id'],
            'name': inst['name'],
            'teamname': team['nickname'],
            'chalname': chal['name'],
            'ip': inst['ip'],
            'status': inst['status'],
            'password': inst['password']
        })
    return jsonify({
        'total':len(instances),
        'instances':instances
    })


@login_required
@teams.route('/team/chals')
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



@teams.route('/team/attack')
@login_required
def attack_record():
    if not session.has_key("record"):
        session["record"]=0
    record=redis_store.lrange("attack",session["record"],-1)
    ans=[]
    for rec in record:
        ans.append(json.loads(rec))
    session['record']=session['record']+len(ans)
    return jsonify({
        "total":len(ans),
        "attacks":ans
    })

@teams.route('/logout',methods=['POST'])
@login_required
def team_logout():
    session.clear()
    return jsonify({
        'code':200,
        'msg':'已注销登录'
    })