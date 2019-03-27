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
启动web服务
* 运行
```bash
python docker_serv.py
```
启动docker管理进程
* 运行 `python manager.py init_manager username password`可添加一个管理员账号
* 访问`/admin`即可登录，之后可添加用户等等

### 题目镜像要求

* 开放ssh服务，并添加`config.py`中指定的user
* 提供启动指令与更新flag指令,其中更新flag指令中flag可以写`flag{test}`，程序运行中将替换为flag，例：
`/bin/bash -c "echo flag{test}>/flag"`

### tips

* 目前版本尽量不要同一浏览器内同时登录管理员和用户
* 由于某些队伍界面的接口直接从redis中获取数据，所以服务启动后请先登录管理员
* 如有搭建问题请详询本人(QQ1223530366)
