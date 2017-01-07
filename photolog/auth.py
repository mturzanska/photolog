from functools import wraps

import bcrypt
from flask import redirect, flash, session, url_for


class AuthError(Exception):
    pass


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def check_password(password, pass_hash):
    return bcrypt.checkpw(password.encode('utf-8'), pass_hash)


def authenticate_user(user, password):
    if not check_password(password, user.password_hash):
        raise AuthError('Bad password')
    return user


def login_required(f):
    @wraps(f)
    def decorate_view(*args, **kwargs):
        if session.get('user_id', None) is None:
            flash('Please log in', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorate_view
