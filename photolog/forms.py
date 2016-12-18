from flask_wtf import Form
from wtforms import StringField, SelectField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired

from photolog.models import Albums


class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    passwo = StringField('passwo', validators=[DataRequired()])


class AlbumForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description')
    status = SelectField('status',
                         choices=Albums.statuses,
                         coerce=int,
                         default=0)

    photos = FileField('photos',
                       render_kw={'multiple': True},
                       validators=[FileAllowed(
                           ['jpg', 'png'], 'JPG or PNG only!')])
