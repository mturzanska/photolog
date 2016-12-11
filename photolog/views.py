from flask import url_for, redirect, render_template, session

from photolog import photolog, db
from photolog.auth import authenticate_user, AuthError
from photolog.forms import LoginForm


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
            user = authenticate_user(
                db.session, form.username.data, form.passwo.data
            )
            session['user_id'] = user.id
            return redirect(url_for('futon'))
        except AuthError:
            return redirect(url_for('login'))
    return render_template('login.html', title='IN', form=form)


@photolog.route('/out', methods=['GET'])
def logout():
    session.clear()
    return render_template('logout.html', title='OUT')


@photolog.route('/futon', methods=['GET', 'POST'])
def futon():
    pass
