from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


photolog = Flask(__name__)
photolog.config.from_object('config')
db = SQLAlchemy(photolog)

from photolog import models
