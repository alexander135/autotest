from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class CommentForm(FlaskForm):
    comment = StringField('Comment')
    submit = SubmitField('Submit')
    
class OptionsForm(FlaskForm):
    bot = IntegerField('Red', [DataRequired()])
    top = IntegerField('Yellow', [DataRequired()])
    count = IntegerField('Data count',[DataRequired()] )
    submit = SubmitField('Submit')
