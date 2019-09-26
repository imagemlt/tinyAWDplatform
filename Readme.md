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
* 运行
```bash
python flag_serv.py
```
启动flag服务进程
* 运行 `python manager.py init_manager username password`可添加一个管理员账号
* 访问`/admin`即可登录，之后可添加用户等等

### 题目镜像要求

* 开放ssh服务，并添加`config.py`中指定的user
* 提供启动指令与更新flag指令,启动指令默认为空，只针对某些特殊镜像使用；其中更新flag指令中flag可以写`flag{test}`，程序运行中将替换为flag，例：
`/bin/bash -c "echo flag{test}>/flag"`
* 镜像中起ssh服务的操作方法可以参考2018年ciscn buildit的模板[https://github.com/CyberPeace/ciscn2018-template](https://github.com/CyberPeace/ciscn2018-template)
* 建议镜像最好可以直接不用添加命令参数启动，具体参考[这个烂尾了的项目里面的写法](https://github.com/imagemlt/CTF_web_dockers)

### tips

* 目前版本尽量不要同一浏览器内同时登录管理员和用户
* 由于某些队伍界面的接口直接从redis中获取数据，所以服务启动后请先登录管理员
* 如有搭建问题请详询本人(QQ1223530366)
