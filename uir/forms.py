from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    comment = StringField('Comment', [Length(max = 20)])
    submit = SubmitField('Submit')
    
class OptionsForm(FlaskForm):
    bot = IntegerField('Red', [DataRequired()])
    top = IntegerField('Yellow', [DataRequired()])
    count = IntegerField('Data count',[DataRequired()] )
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    login = StringField("Login", [DataRequired()])
    password = PasswordField("Password", [DataRequired()])
    submit = SubmitField('Submit')
