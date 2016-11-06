from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


photolog = Flask(__name__)
photolog.config.from_object('photolog.config')
db = SQLAlchemy(photolog)

from photolog import models, views
