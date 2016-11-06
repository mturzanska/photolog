from photolog import db


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password_hash = db.Column(db.Text)
    inserted_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    albums = db.relationship('Albums')


class Albums(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    status = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey(users.id), index=True)
    inserted_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    photos = db.relationship('Photos')


class Photos(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.Text)
    file_name = db.Column(db.Text)
    description = db.Column(db.Text)
    album_id = db.Column(db.Integer, db.ForeignKey(albums.id), index=True)
    inserted_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
