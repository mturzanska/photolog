from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect


photolog = Flask(__name__)
photolog.config.from_object('photolog.config')
csrf = CsrfProtect()
csrf.init_app(photolog)
db = SQLAlchemy(photolog)

from photolog import models, views
db.create_all()
