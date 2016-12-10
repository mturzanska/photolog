import unittest as t

from photolog.models import Users, Albums, Photos
from photolog.auth import hash_password
from photolog import db


class ModelHelper():
    def __init__(self, db_session):
        self.session = db_session

    def create_user(self, username='bob', password='123123123', add=True):
        password_hash = hash_password(password)
        user = Users(username=username, password_hash=password_hash)
        if add:
            self.session.add(user)
            self.session.commit()
        return user

    def create_album(self, user, name='album', desc='Album Desc', status=0):
        album = Albums(name=name, description=desc, status=status)
        self.session.add(album)
        self.session.commit()
        user.albums.append(album)
        return album

    def create_photo(self, album, name='photo'):
        photo = Photos(name=name, album=album)
        self.session.add(photo)
        self.session.commit()
        album.photos.append(photo)
        return photo


class PhotologTestCase(t.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_helper = ModelHelper(db.session)


def bytes_encode(msg):
    return bytes(msg, encoding='utf-8')
