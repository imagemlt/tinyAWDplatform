# -*- coding: UTF-8 -*-
from AWD import create_app
from config import config



app=create_app(config['default'])

if __name__ == '__main__':
    app.run()
