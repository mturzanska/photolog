from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from photolog.filters import jinja2_nice_datetime


photolog = Flask(__name__, static_folder='../public')
photolog.config.from_object('photolog.config')
csrf = CsrfProtect()
csrf.init_app(photolog)
db = SQLAlchemy(photolog)

photolog.jinja_env.filters['nice_datetime'] = jinja2_nice_datetime

from photolog import models, views
db.create_all()
