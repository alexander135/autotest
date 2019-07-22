from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length
from wtforms import widgets

class CommentForm(FlaskForm):
    comment = StringField('Comment', [Length(max = 20)])
    submit = SubmitField()
    
class OptionsForm(FlaskForm):
    bot = IntegerField('Red', [DataRequired()])
    top = IntegerField('Yellow', [DataRequired()])
    count = IntegerField('Data count',[DataRequired()] )
    submit = SubmitField()

class LoginForm(FlaskForm):
    login = StringField("Login", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField('Submit')

class ConfigForm(FlaskForm):
    config = TextAreaField("Config", [DataRequired()])
    submit = SubmitField("Submit")

