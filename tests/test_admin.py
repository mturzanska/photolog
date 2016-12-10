import unittest as t
from unittest.mock import patch
from io import BytesIO
import json

from flask import url_for

from tests.test_helpers import PhotologTestCase, bytes_encode
from photolog import db
from photolog import photolog as app
from photolog.models import Albums, Photos


def setUpModule():
    app.config['SERVER_NAME'] = 'example.com'
    app.config['SECRET_KEY'] = 'IAMASECRETKEYSSSSSHHH'
    app.config['WTF_CSRF_ENABLED'] = False


class AdminTest(PhotologTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with app.app_context():
            cls.admin_url = url_for('futon')

    def setUp(self):
        db.create_all()
        self.c = app.test_client()
        self.user = self.model_helper.create_user('bob', '123123')
        # authenticate user
        # authentication decorator
        self.album = self.model_helper.create_album(self.user,
                                                    name='Test album 1')

    def tearDown(self):
        db.drop_all()

    def test_admin_index_shows_all_albums(self):
        album_name = 'test_album 2'
        self.model_helper.create_album(self.user, name=album_name)
        rsp = self.c.get(self.admin_url)

        self.assertIn(bytes_encode(self.album.name), rsp.data)
        self.assertIn(bytes_encode(album_name), rsp.data)

    def test_edit_page_has_filled_out_form(self):
        with app.app_context():
            url = url_for('futon_edit_album', album_id=self.album.id)
        rsp = self.c.get(url)

        self.assertIn(bytes_encode(self.album.name), rsp.data)
        self.assertIn(bytes_encode(self.album.description), rsp.data)

    def test_edit_page_contains_photo_names(self):
        with app.app_context():
            url = url_for('futon_edit_album', album_id=self.album.id)
        photo_1 = self.model_helper.create_photo(self.album, name='photo 1')
        photo_2 = self.model_helper.create_photo(self.album, name='photo 2')

        rsp = self.c.get(url)

        self.assertIn(bytes_encode(photo_1.name), rsp.data)
        self.assertIn(bytes_encode(photo_2.name), rsp.data)

    def test_new_album_page_has_blank_form(self):
        with app.app_context():
            url = url_for('futon_new_album')
        rsp = self.c.get(url)

        self.assertEqual(rsp.status_code, 200)
        self.assertIn(bytes_encode('New Album'), rsp.data)

    def test_new_page_post_creates_new_album_and_redirects_to_it(self):
        with app.app_context():
            url = url_for('futon_new_album')
        album = {'name': 'New Album Test'}
        rsp = self.c.post(url, data=album)

        album_db = self.model_helper.session.query(Albums).order_by(
            Albums.id.desc()).first()

        with app.app_context():
            album_url = url_for('futon_edit_album', album_id=album_db.id)

        self.assertEqual(rsp.status_code, 302)
        self.assertEqual(rsp.headers.get('location'), album_url)
        self.assertEqual(album_db.name, album['name'])

    def test_edit_page_post_updates_an_existing_album(self):
        with app.app_context():
            url = url_for('futon_edit_album', album_id=self.album.id)
        album_update = {'name': 'Edit Album Test', 'status': 1}
        rsp = self.c.post(url, data=album_update)

        self.assertEqual(rsp.status_code, 302)

        updated_album = self.model_helper.session.query(Albums).filter(
            Albums.id == self.album.id).first()
        self.assertEqual(updated_album.name, album_update['name'])

    @patch('photolog.views.process_file')
    def test_edit_page_upload_single_file_saves_files(self, process_mock):
        with app.app_context():
            url = url_for('futon_edit_album', album_id=self.album.id)

        with open('photolog/static/photolog_test.png', 'rb') as f:
            img = BytesIO()
            img.write(f.read())
            img.seek(0)
            data = {'name': 'Edit Test Album with file',
                    'photos[]': [(img,
                                 'test.png', )]}
        rsp = self.c.post(url, data=data)

        self.assertEqual(rsp.status_code, 302)

        updated_album = self.model_helper.session.query(Albums).filter(
            Albums.id == self.album.id).one()

        self.assertEqual(updated_album.photos.count(), 1)

    @patch('photolog.views.process_file')
    def test_edit_page_upload_multiple_files_saves_files(self, process_mock):
        with app.app_context():
            url = url_for('futon_edit_album', album_id=self.album.id)
        files = ['photolog/static/photolog_test.png',
                 'photolog/static/photolog_test_2.png']
        data = {'name': 'Edit Test Album with files', 'photos[]': []}

        for i, f_name in enumerate(files):
            with open(f_name, 'rb') as f:
                img = BytesIO()
                img.write(f.read())
                img.seek(0)
                data['photos[]'].append((img, 'test_{}.png'.format(i),))
        rsp = self.c.post(url, data=data)

        self.assertEqual(rsp.status_code, 302)

        updated_album = self.model_helper.session.query(Albums).filter(
            Albums.id == self.album.id).one()

        self.assertEqual(updated_album.name, 'Edit Test Album with files')
        self.assertEqual(updated_album.photos.count(), 2)

        for i, photo in enumerate(updated_album.photos.all()):
            self.assertEqual(photo.file_name, 'test_{}.png'.format(i))

    @patch('photolog.views.process_file')
    def test_new_page_upload_multiple_files_saves_files(self, process_mock):
        with app.app_context():
            url = url_for('futon_new_album', album_id=self.album.id)
        files = ['photolog/static/photolog_test.png',
                 'photolog/static/photolog_test_2.png']
        data = {'name': 'New Test Album with files', 'photos[]': []}

        for i, f_name in enumerate(files):
            with open(f_name, 'rb') as f:
                img = BytesIO()
                img.write(f.read())
                img.seek(0)
                data['photos[]'].append((img, 'test_{}.png'.format(i),))
        rsp = self.c.post(url, data=data)

        self.assertEqual(rsp.status_code, 302)

        album_from_db = self.model_helper.session.query(Albums).order_by(
            Albums.id.desc()).first()

        self.assertEqual(album_from_db.photos.count(), 2)

        for i, photo in enumerate(album_from_db.photos.all()):
            self.assertEqual(photo.file_name, 'test_{}.png'.format(i))

    def test_update_photos_updates_photo_records_and_redirects(self):
        with app.app_context():
            url = url_for('futon_update_photos', album_id=self.album.id)
        photo_1 = self.model_helper.create_photo(self.album, name='photo-1')
        photo_2 = self.model_helper.create_photo(self.album, name='photo-2')
        data = json.dumps({'photo_updates': [
            {'id': photo_1.id,
             'name': 'photo-1-update'},
            {'id': photo_2.id,
             'name': 'photo-2-update'}
        ]})

        rsp = self.c.post(url,
                          data=data,
                          content_type='application/json')

        self.assertEqual(rsp.status_code, 302)
        photo_1 = self.model_helper.session.merge(photo_1)
        photo_2 = self.model_helper.session.merge(photo_2)

        self.assertEqual(photo_1.name, 'photo-1-update')
        self.assertEqual(photo_2.name, 'photo-2-update')

    def test_update_photos_deletes_photos_and_redirects(self):
        with app.app_context():
            url = url_for('futon_update_photos', album_id=self.album.id)
        photo_1 = self.model_helper.create_photo(self.album, name='photo-1')
        photo_2 = self.model_helper.create_photo(self.album, name='photo-2')
        data = json.dumps({'photo_updates': [
            {'id': photo_1.id,
             'name': 'photo-1-delete',
             'delete': "true"},
            {'id': photo_2.id,
             'name': 'photo-2-update'}
        ]})

        rsp = self.c.post(url,
                          data=data,
                          content_type='application/json')
        self.assertEqual(rsp.status_code, 302)

        photo_2 = self.model_helper.session.merge(photo_2)
        album_updated = self.model_helper.session.merge(self.album)

        self.assertEqual(photo_2.name, 'photo-2-update')
        self.assertEqual(album_updated.photos.count(), 1)
        self.assertEqual(Photos.query.count(), 1)

    def test_delete_album_deletes_album_and_redirects(self):
        with app.app_context():
            url = url_for('futon_delete_album', album_id=self.album.id)

        self.model_helper.create_album(self.user, name='album-2')
        self.model_helper.create_photo(self.album)

        rsp = self.c.post(url)

        self.assertEqual(rsp.status_code, 302)
        self.assertEqual(Albums.query.count(), 1)
        self.assertEqual(Albums.query.first().name, 'album-2')
