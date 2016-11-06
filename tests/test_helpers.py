from photolog.models import Users, Albums, Photos
from photolog.auth import hash_password


class ModelHelper():
    def __init__(self, db_session):
        self.session = db_session

    def create_user(self, username='bob', password='123123123'):
        password_hash = hash_password(password)
        user = Users(username=username, password_hash=password_hash)
        self.session.add(user)
        self.session.commit()
        return user

    def create_album(self, user, name='album'):
        album = Albums(name=name, user=user)
        self.session.add(album)
        self.session.commit()
        return album

    def create_photo(self, album, name='photo'):
        photo = Photos(name=name, album=album)
        self.session.add(photo)
        self.session.commit()
        return photo
