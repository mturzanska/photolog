import os

WTF_CSRF_ENABLED = True
SQLALCHEMY_DATABASE_URI = os.environ['PHOTOLOG_DB_URI']
SERVER_NAME = os.environ.get('SERVER_NAME')
WTF_CSRF_SECRET_KEY = 'not_so_secret'
SECRET_KEY = 'not_so_secter_either'
