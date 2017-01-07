from flask import render_template, redirect, url_for, flash, request, session
from flask.views import MethodView
from sqlalchemy.orm.exc import NoResultFound

from photolog import photolog, db
from photolog.auth import (authenticate_user, AuthError, hash_password,
                           login_required)
from photolog.config import ITEMS_PER_PAGE
from photolog.forms import LoginForm, AlbumForm
from photolog.models import Albums, Users, Photos
from photolog.pics import save_to_album


@photolog.route('/', methods=['GET'])
@photolog.route('/<int:page>', methods=['GET'])
def index(page=1):
    albums = Albums.query.paginate(page, ITEMS_PER_PAGE, False).items
    return render_template('index.html', title='photolog', albums=albums)


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
@login_required
def logout():
    session.clear()
    return render_template('logout.html', title='OUT')


@photolog.route('/futon')
@login_required
def futon():
    albums = Albums.query.all()
    return render_template('admin/index.html', albums=albums)


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
            save_to_album(request.files.getlist('photos[]'), album)

            db.session.commit()
            return redirect(url_for('futon_edit_album', album_id=album.id))
        flash('Error when trying to validate form', 'error')
        return render_template('admin/edit.html',
                               album=album,
                               album_form=album_form)


photolog.add_url_rule(
    '/futon/<int:album_id>/edit',
    view_func=login_required(FutonEditAlbum.as_view('futon_edit_album')))


class FutonNewAlbum(MethodView):
    def get(self):
        album_form = AlbumForm()
        return render_template('admin/new.html', album_form=album_form)

    def post(self):
        album_form = AlbumForm()

        if album_form.validate_on_submit():
            album = Albums()
            album_form.populate_obj(album)
            album.user_id = session.get('user_id')
            db.session.add(album)
            save_to_album(request.files.getlist('photos[]'), album)

            db.session.commit()
            return redirect(url_for('futon_edit_album', album_id=album.id))
        flash('Error when trying to validate new album', 'error')
        return render_template('admin/new.html', album_form=album_form)


photolog.add_url_rule(
    '/futon/new',
    view_func=login_required(FutonNewAlbum.as_view('futon_new_album')))


@photolog.route('/futon/<int:album_id>/update-photos', methods=['POST'])
@login_required
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


@photolog.route('/futon/<int:album_id>/delete', methods=['GET'])
@login_required
def futon_delete_album(album_id):
    album = Albums.query.filter_by(id=album_id).first_or_404()
    db.session.delete(album)
    db.session.commit()

    flash('Album {0} deleted!'.format(album.name), 'success')
    return redirect(url_for('futon'))
