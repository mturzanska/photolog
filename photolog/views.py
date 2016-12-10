from functools import wraps

from os.path import join as path_join
from flask import render_template, redirect, url_for, flash, request, session
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound

from photolog import photolog, db
from photolog.auth import authenticate_user, AuthError, hash_password
from photolog.forms import LoginForm, AlbumForm
from photolog.models import Albums, Photos


def login_required(f):
    @wraps(f)
    def decorate_view(*args, **kwargs):
        if session.get('user_id', None) is None:
            flash('Please log in', 'error')
            return redirect(url_for('futon'))
        return f(*args, **kwargs)
    return decorate_view


@photolog.route('/')
def home():
    photos = [
        {
            'created_at': 'created at some time ago',
            'filename': '/static/photolog_test.png',
         },
        {
            'created_at': 'created at some time ago',
            'filename': '/static/photolog_test_2.png',
         },
        {
            'created_at': 'created at some time ago',
            'filename': '/static/photolog_test_3.jpg',
         },
    ]
    return render_template('home.html', title='photolog', photos=photos)


@photolog.route('/in', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = db.session.query(Users) \
                             .filter(Users.username == form.username.data) \
                             .one()
        except NoResultFound:
            hash_password('dummy password')
            return redirect(url_for('login'))
        try:
            authenticate_user(user, form.passwo.data)
        except AuthError:
            return redirect(url_for('login'))
        session['user_id'] = user.id
        return redirect(url_for('futon'))
    return render_template('login.html', title='IN', form=form)


@photolog.route('/out', methods=['GET'])
def logout():
    session.clear()
    return render_template('logout.html', title='OUT')


@photolog.route('/futon')
def futon():
    albums = Albums.query.all()
    return render_template('admin/index.html', albums=albums)


def process_file(dest, file_storage):
    file_storage.save(path_join(dest, file_storage.filename))


def save_images_to_album(img_file_storages, album):
    for img in img_file_storages:
        photo = Photos(file_name=img.filename, album_id=album.id)
        album.photos.append(photo)
        db.session.add(photo)
        process_file(photolog.config['UPLOAD_FOLDER'], img)


class FutonEditAlbum(MethodView):
    def get(self, album_id):
        album = Albums.query.filter_by(id=album_id).first_or_404()
        album_form = AlbumForm(obj=album)
        return render_template('admin/edit.html',
                               album=album,
                               album_form=album_form)

    def post(self, album_id):
        album_form = AlbumForm()
        album = Albums.query.filter_by(id=album_id).first_or_404()

        if album_form.validate_on_submit():
            album_form.populate_obj(album)
            save_images_to_album(request.files.getlist('photos[]'), album)

            db.session.commit()
            return redirect(url_for('futon_edit_album', album_id=album.id))
        flash('Error when trying to validate form', 'error')
        return render_template('admin/edit.html',
                               album=album,
                               album_form=album_form)


photolog.add_url_rule('/futon/<int:album_id>/edit',
                      view_func=FutonEditAlbum.as_view('futon_edit_album'))


class FutonNewAlbum(MethodView):
    def get(self):
        album_form = AlbumForm()
        return render_template('admin/new.html', album_form=album_form)

    def post(self):
        album_form = AlbumForm()

        if album_form.validate_on_submit():
            album = Albums()
            album_form.populate_obj(album)
            # tmp
            album.user_id = 1
            db.session.add(album)
            save_images_to_album(request.files.getlist('photos[]'), album)

            db.session.commit()
            return redirect(url_for('futon_edit_album', album_id=album.id))
        flash('Error when trying to validate new album', 'error')
        return render_template('admin/new.html', album_form=album_form)


photolog.add_url_rule('/futon/new',
                      view_func=FutonNewAlbum.as_view('futon_new_album'))


@photolog.route('/futon/<int:album_id>/update-photos', methods=['POST'])
def futon_update_photos(album_id):
    photo_updates = request.get_json().get('photo_updates', [])
    for update in photo_updates:
        photo_id = update.pop('id')
        if update.pop('delete', None) == 'true':
            Photos.query.filter_by(id=photo_id).delete()
        else:
            Photos.query.filter_by(id=photo_id).update(update)
    db.session.commit()

    return redirect(url_for('futon_edit_album', album_id=album_id))


@photolog.route('/futon/<int:album_id>/delete', methods=['POST'])
def futon_delete_album(album_id):
    album = Albums.query.filter_by(id=album_id).first_or_404()
    db.session.delete(album)
    db.session.commit()

    flash('Album {0} deleted!'.format(album.name), 'success')
    return redirect(url_for('futon'))
