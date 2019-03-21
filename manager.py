# -*- coding: UTF-8 -*-
from flask_script import Manager
from AWD import create_app
from config import config
from AWD.models import db,Admin
import hashlib

app=create_app(config['default'])

manager=Manager(app)

@manager.command
def init_manager(username,password):
    'init manager'
    md5 = hashlib.md5()
    md5.update(password)
    pwd = md5.hexdigest()
    admin = Admin(username, pwd)
    db.session.add(admin)
    db.session.commit()
    print "[+]admin user %s created"%username

if __name__=='__main__':
    manager.run()