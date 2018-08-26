# -*- coding: UTF-8 -*-
from flask import Blueprint


views=Blueprint('views',__name__)

@views.route('/views')
def index():
    return '<h1>this is view blueprint!</h1>'