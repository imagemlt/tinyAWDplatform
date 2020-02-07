# tinyAWDplatform

基于docker运行在单机上的awd平台，仅适用于小规模的队内练习使用.  

### 技术架构：
* docker-py
* flask
* redis
* vue+elementui（后台与用户界面均基于[https://github.com/taylorchen709/vue-admin](https://github.com/taylorchen709/vue-admin)）


### 依赖：
* flask
* flask_wtf
* flask_redis
* redis
* docker

### 使用方法

* 运行
```bash
python serve.py
```
启动web服务，或者使用gunicorn启动：
```
gunicorn -b 127.0.0.1:5000 serve:app
```
* 运行
```bash
python docker_serv.py
```
启动docker管理进程
* 运行
```bash
python flag_serv.py
```
启动flag服务进程
* 运行 `python manager.py init_manager username password`可添加一个管理员账号
* 访问`/admin`即可登录，之后可添加用户等等

### 题目镜像要求
> 示例镜像dockerfile: https://github.com/susers/tinyAWD_chals

* 开放ssh服务，并添加`config.py`中指定的user
* 提供启动指令与更新flag指令,启动指令默认为空，只针对某些特殊镜像使用；其中更新flag指令中flag可以写`flag{test}`，程序运行中将替换为flag，例：
`/bin/bash -c "echo flag{test}>/flag"`
* 镜像中起ssh服务的操作方法可以参考2018年ciscn buildit的模板[https://github.com/CyberPeace/ciscn2018-template](https://github.com/CyberPeace/ciscn2018-template)
* 建议镜像最好可以直接不用添加命令参数启动

### flag提交接口

请求`/flag?from=攻击id&flag=YOUR FLAG`即可，其中攻击id为登陆后个人信息栏的攻击id

### 配置文件说明

配置文件位于`config.py`,需要修改的地方有：
* SECRET_KEY, 使用默认值可能会导致cookie伪造等。
```
SECRET_KEY = os.environ.get('SECRET_KEY') or '\xb1\xca\xb2\x00P\xd0\x14#\xff0\xe50d\x88\xc3\xf5\xcc\x90W!\x96\xf8%U'
```
* 数据库，如果想要使用mysql或者其他数据库需修改此配置
```
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///{}/ctfd.db'.format(basedir)
```
* redis连接地址,最好为redis添加密码以防未授权访问
```
 REDIS_URL='redis://localhost:6379/0'
```
* docker_config相关
```
docker_config={
    'redis_host':'localhost',# redis相关配置
    'redis_port':6379,
    'redis_db':0,
    'redis_password':None,
    'baseurl':'unix://var/run/docker.sock', # docker api 连接地址，尽量避免未授权访问
    'network_name':'awd_test', # docker network名称
    'network_prefix':'192.25', # ip地址段
    'flag_prefix':'SUSCTF', # flag前缀
    'expire':60, # flag不能重复提交的锁定时间，尽量>=flag更新时间间隔，单位为秒
    'time_interval':60, # 多长时间换一轮flag，单位为秒
    'ssh_user':'ciscn' # ssh用户名，需要与题目镜像中的相同
}
```

### tips

* 目前版本尽量不要同一浏览器内同时登录管理员和用户
* 由于某些队伍界面的接口直接从redis中获取数据，所以服务启动后请先登录管理员
* 正式环境最好使用gunicorn启动
* redis最好添加密码
* 如有搭建问题请详询本人(QQ1223530366)
