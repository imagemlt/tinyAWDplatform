from flask import Flask
from flask_wtf.csrf import generate_csrf,CSRFProtect
from flag import flag
from views import views
from models import db,Admin
from admin import admin
from redisConn import redis_store
from teams import teams
import hashlib

blueprint_list=[flag,views,admin,teams]


def create_app(config):
    app=Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    db.create_all(app=app)
    redis_store.init_app(app)
    CSRFProtect(app)
    for m in blueprint_list:
        app.register_blueprint(m)
    @app.route('/init_a_manager')
    def index():
        md5 = hashlib.md5()
        md5.update('xxx')
        pwd = md5.hexdigest()
        admin = Admin('imagemlt', pwd)
        db.session.add(admin)
        db.session.commit()
        return '<h1>this is index</h1>'
    @app.after_request
    def after_request(response):
        csrf_token=generate_csrf()
        response.set_cookie("XSRF-TOKEN",csrf_token)
        return response
    return app
