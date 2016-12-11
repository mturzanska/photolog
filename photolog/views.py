from flask import url_for, redirect, render_template, session
from sqlalchemy.orm.exc import NoResultFound

from photolog import photolog, db
from photolog.auth import authenticate_user, AuthError, hash_password
from photolog.forms import LoginForm
from photolog.models import Users


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
            try:
                raise AuthError('User not found')
            except AuthError:
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


@photolog.route('/futon', methods=['GET', 'POST'])
def futon():
    pass
