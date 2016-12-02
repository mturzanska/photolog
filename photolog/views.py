from flask import render_template

from photolog import photolog


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
