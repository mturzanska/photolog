import unittest as t

from flask import url_for

from tests.test_helpers import ModelHelper
from photolog import db
from photolog import photolog as app
import photolog.auth as auth
from photolog.models import Albums


class AuthTest(t.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_helper = ModelHelper(db.session)

    def setUp(self):
        db.create_all()
        self.username = 'bob'
        self.password = 'password123'
        self.user = self.model_helper.create_user(self.username, self.password)

    def tearDown(self):
        db.drop_all()

    def test_authenticate_user_success(self):
        try:
            user = auth.authenticate_user(self.user, self.password)
        except auth.AuthError:
            self.failed('failed to authenticate user')
        self.assertEqual(user, self.user)

    def test_authenticate_user_doesnt_exist(self):
        with self.assertRaises(auth.AuthError):
            bad_user = self.model_helper.create_user(
                username='mallory', add=False
            )
            auth.authenticate_user(bad_user, self.password)

    def test_authenticate_user_bad_password(self):
        with self.assertRaises(auth.AuthError):
            auth.authenticate_user(self.user, 'bob123')


class SessionViewTest(t.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['TESTING'] = True
        cls.model_helper = ModelHelper(db.session)
        with app.app_context():
            cls.login_url = url_for('login')
            cls.logout_url = url_for('logout')
            cls.admin_url = url_for('futon')

    def setUp(self):
        db.create_all()
        self.c = app.test_client()
        self.username = 'bob'
        self.password = 'password123'
        self.user = self.model_helper.create_user(self.username, self.password)

    def tearDown(self):
        db.drop_all()

    def test_login_success_redirects(self):
        rsp = self.c.post(self.login_url,
                          data={'username': self.username,
                                'passwo': self.password})
        headers = rsp.headers

        self.assertEqual(rsp.status_code, 302)
        self.assertEqual(headers['location'], self.admin_url)

    def test_login_success_sets_session(self):
        self.c.post(self.login_url,
                    data={'username': self.username,
                          'passwo': self.password})

        with self.c.session_transaction() as sess:
            self.assertTrue('user_id' in sess)
            self.assertEqual(sess['user_id'], self.user.id)

    def test_login_failure_bad_password_redirect(self):
        rsp = self.c.post(self.login_url,
                          data={'username': self.username,
                                'passwo': 'bad_passwors'})
        headers = rsp.headers

        self.assertEqual(rsp.status_code, 302)
        self.assertEqual(headers['location'], self.login_url)

    def test_login_failure_bad_user_redirect(self):
        rsp = self.c.post(self.login_url,
                          data={'username': 'bad_user',
                                'passwo': self.password})
        headers = rsp.headers

        self.assertEqual(rsp.status_code, 302)
        self.assertEqual(headers['location'], self.login_url)

    def test_logout_clears_session(self):
        self.c.get(self.logout_url)

        with self.c.session_transaction() as sess:
            self.assertTrue('user_id' not in sess)


class AdminTest(t.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model_helper = ModelHelper()

    def setUp(self):
        db.create_all()
        self.c = app.test_client()
        self.user = self.model_helper.create_user('bob', '123123')
        self.album = self.model_helper.create_album(user=self.user,
                                                    name='Test album 1')

    def tearDown(self):
        db.drop_all()

    def test_admin_index_shows_all_albums(self):
        self.model_helper.insert_album(user=self.user, title='test album 2')
        rsp = self.c.get('/')

        self.assertIn(self.album.title, rsp.data)
        self.assertIn('test album 2', rsp.data)

    def test_edit_page_has_filled_out_form(self):
        url = url_for('admin_edit_album', id=self.album.id)
        rsp = self.c.get(url)

        self.assertIn(self.album.title, rsp.data)

    def test_edit_page_has_all_album_statuses(self):
        pass

    def test_new_album_page_has_blank_form(self):
        url = url_for('admin_new_album')
        rsp = self.c.get(url)

        self.assertIn(url_for('new_album', rsp))

    def test_new_page_post_creates_new_album_and_redirects_to_it(self):
        url = url_for('admin_create_album')
        album = {'title': 'New Album Test'}
        rsp = self.c.post(url, data=album)

        album_db = self.model_helper.session.query(Albums).order_by(
            Albums.id).first()
        album_url = url_for('admin_edit_album', id=album_db.id)

        self.assertEqual(rsp.status_code, 302)
        self.assertEqual(rsp.headers.get('location'), album_url)
        self.assertEqual(album_db.title, album['title'])

    def test_edit_page_post_updates_an_existing_album(self):
        url = url_for('admin_edit_album', id=self.album.id)
        album = {'title': 'Edit Album Test'}
        rsp = self.c.post(url, data=album)

        updated_album = self.model_helper.session.query(Albums).filter(
            Albums.id == album.id).first()
        self.assertEqual(updated_album.title, album['title'])

    def test_edit_page_upload_single_file_saves_files(self):
        pass

    def test_edit_page_upload_multiple_files_saves_files(self):
        pass

    def test_new_page_upload_multiple_files_saves_files(self):
        pass

    def test_update_photos_updates_photo_records_and_redirects(self):
        pass

    def test_update_photos_deletes_photos_and_redirects(self):
        pass


if __name__ == '__main__':
    t.main()
