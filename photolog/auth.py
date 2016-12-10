import bcrypt
from sqlalchemy.orm.exc import NoResultFound

from photolog.models import Users


class AuthError(Exception):
    pass


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def check_password(password, pass_hash):
    return bcrypt.checkpw(password.encode('utf-8'), pass_hash)


def authenticate_user(db_session, username, password):
    try:
        user = db_session.query(Users).filter(Users.username == username).one()
    except NoResultFound:
        hash_password('dummy password')
        raise AuthError('User not found')

    if check_password(password, user.password_hash):
        return user
    else:
        raise AuthError('Bad password')
