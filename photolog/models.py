from datetime import datetime

from photolog import db


def timestamp():
    return datetime.utcnow()


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text)
    inserted_at = db.Column(db.DateTime,
                            nullable=False,
                            default=timestamp)
    updated_at = db.Column(db.DateTime,
                           nullable=True,
                           onupdate=timestamp)

    albums = db.relationship('Albums')


class Albums(db.Model):
    __tablename__ = 'albums'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    status = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id), index=True)
    inserted_at = db.Column(db.DateTime,
                            nullable=False,
                            default=timestamp)
    updated_at = db.Column(db.DateTime,
                           nullable=True,
                           onupdate=timestamp)

    photos = db.relationship('Photos')


class Photos(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.Text)
    file_name = db.Column(db.Text)
    description = db.Column(db.Text)
    album_id = db.Column(db.Integer, db.ForeignKey('albums.id'), index=True)
    album_id = db.Column(db.Integer, db.ForeignKey(Albums.id), index=True)
    inserted_at = db.Column(db.DateTime,
                            nullable=False,
                            default=timestamp)
    updated_at = db.Column(db.DateTime,
                           nullable=True,
                           onupdate=timestamp)
