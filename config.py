# -*- coding: UTF-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '\xb1\xca\xb2\x00P\xd0\x14#\xff0\xe50d\x88\xc3\xf5\xcc\x90W!\x96\xf8%U'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///{}/ctfd.db'.format(basedir)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = '/tmp/flask_session'
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 604800
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                    'uploads')
    LOG_FOLDER = os.environ.get('LOG_FOLDER') or os.path.join(basedir, 'logs')
    REDIS_URL='redis://localhost:6379/0'
    TEMPLATES_AUTO_RELOAD = True
    

class DevelopmentConfig(Config):
    DEBUG=True

class TestingConfig(Config):
    TESTING=True

class ProductionConfig(Config):
    DEBUG=False
    TESTING=False

config={
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production':ProductionConfig,
    'default':DevelopmentConfig
}

docker_config={
    'redis_host':'localhost',
    'redis_port':6379,
    'redis_db':0,
    'redis_password':None,
    'baseurl':'unix://var/run/docker.sock',
    'network_name':'awd_test',
    'network_prefix':'192.25',
    'flag_prefix':'SUSCTF',
    'expire':60,
    'time_interval':60,
    'ssh_user':'ciscn'
}
