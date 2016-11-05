import unittest as t
from test import app

import test_helpers as h

from lib import auth


class AuthTest(t.TestCase):
    def setUp(self):
        self.username = 'bob'
        self.password = 'password123'
        self.user = h.create_user(self.username, self.password)

    def test_authenticate_user_success(self):
        try:
            auth.login_username_pass(self.username, self.password)
        except auth.AuthError:
            self.failed('failed to authenticate user')

    def test_authenticate_user_doesnt_exist(self):
        with self.assertRaises(auth.AuthError):
            auth.login_username_pass('mallory', self.password)

    def test_authenticate_user_bad_password(self):
        with self.assertRaises(auth.AuthError):
            auth.login_username_pass(self.username, 'bob123')

    def test_is_user_authenticated(self):
        session = {self.username: self.password}
        result = auth.is_authenticated(session)
        self.assertTrue(result)

    def test_is_user_authenticated_bad_user(self):
        session = {'bob': 'password'}
        result = auth.is_authenticated(session)
        self.assertFalse(result)


class AuthViewsTest(t.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app
        self.c = app.test_client()
        self.username = 'bob'
        self.password = 'password123'
        self.user = h.create_user(self.username, self.password)

    def test_login_success_redirects(self):
        rsp = self.c.post('/hej',
                          data={'username': self.username,
                                'password': self.password})
        headers = rsp.headers

        self.assertEqual(rsp.status_code, 301)
        self.assertEqual(headers['location'], '/gory')

    def test_login_success_sets_session(self):
        rsp = self.c.post('/hej',
                          data={'username': self.username,
                                'password': self.password})

        with  self.c.session_transaction() as sess:
            self.assertTrue('user_id' in sess)
            self.assertEqual(sess['user_id'], self.user['id'])

    def test_login_failure_bad_password_redirect(self):
        rsp = self.c.post('/hej',
                          data={'username': self.username,
                                'password': self.password})
        headers = rsp.headers

        self.assertEqual(rsp.status_code, 301)
        self.assertEqual(headers['location'], '/hej')

    def test_login_failure_bad_user_redirect(self):
        rsp = self.c.post('/hej',
                          data={'username': self.username,
                                'password': self.password})
        headers = rsp.headers

        self.assertEqual(rsp.status_code, 301)
        self.assertEqual(headers['location'], '/hej')

    def test_logout_clears_session(self):
        rsp = self.c.get('/papa')

        with self.c.session_transaction() as sess:
            self.assertTrue('user_id' not in sess)


class AdminTest(t.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app
        self.c = app.test_client()

    def test_admin_index_shows_all_albums(self):
        pass

    def test_edit_page_has_filled_out_form(self):
        pass

    def test_edit_page_has_all_album_statuses(self):
        pass

    def test_new_album_page_has_blank_form(self):
        pass

    def test_new_page_post_creates_new_album_and_redirects_to_it(self):
        pass

    def test_edit_page_post_updates_an_existing_album(self):
        pass

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
