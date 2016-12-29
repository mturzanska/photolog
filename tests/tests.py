import unittest as t

from flask import url_for

from tests.test_helpers import ModelHelper
from photolog import db
from photolog import photolog as app
import photolog.auth as auth

app.config['SERVER_NAME'] = 'example.com'
app.config['SECRET_KEY'] = 'IAMASECRETKEYSSSSSHHH'
app.config['WTF_CSRF_ENABLED'] = False


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

class IndexTest(t.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        db.create_all()
        self.model_helper = ModelHelper(db.session)
        with app.app_context():
            self.index_url_page_1 = url_for('index')
            self.index_url_page_2 = url_for('index', page=2)
            self.c = app.test_client()

    def tearDown(self):
        db.drop_all()

    def test_pagination(self):
        user = self.model_helper.create_user()
        for id in range(1, 20):
            name = 'album_{0}'.format(id)
            self.model_helper.create_album(user, name=name)

        page_1 = self.c.get(self.index_url_page_1)
        self.assertIn('album_10', str(page_1.data))
        self.assertNotIn('album_11', str(page_1.data))
        page_2 = self.c.get(self.index_url_page_2)
        self.assertNotIn('album_10', str(page_2.data))
        self.assertIn('album_11', str(page_2.data))

if __name__ == '__main__':
    t.main()
