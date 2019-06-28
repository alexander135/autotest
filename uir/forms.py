from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class CommentForm(FlaskForm):
    comment = StringField('Comment')
    submit = SubmitField('Submit')
    
class ColorConfigForm(FlaskForm):
    bot = IntegerField('Red', [DataRequired()])
    top = IntegerField('Yellow', [DataRequired()])
    submit = SubmitField('Submit')
