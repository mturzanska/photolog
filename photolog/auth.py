import bcrypt


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
