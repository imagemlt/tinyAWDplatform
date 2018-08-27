# tinyAWDplatform

基于docker运行在单机上的awd平台，仅适用于小规模的队内练习使用.  

### 技术架构：
* docker-py
* flask
* redis
* vue+elementui


### 依赖：
* flask
* flask_wtf
* flask_redis
* redis
* docker-py

### 使用方法

* 运行
```bash
python serve.py
```
启动web服务
* 运行
```bash
python docker_serv.py
```
启动docker管理进程
* 访问`/init_a_manager`可生成一个管理员帐号，具体根据`AWD/__init__.py`中修改

### 题目镜像要求

* 开放ssh服务，并添加`config.py`中指定的user
* 提供启动指令与更新flag指令


