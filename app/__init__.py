from flask import Flask
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
#TO-DO: 'simple' cache is not thread-safe
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

from app import views, models

