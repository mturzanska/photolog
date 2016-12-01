from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_envvar('PHOTOLOG_CONFIG_FILE')
db = SQLAlchemy(app)
db.init_app(app)

from photolog import models
