from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    file = FileField('Upload File', validators=[DataRequired()])
    question = StringField('Enter your question:', validators=[DataRequired()])
    submit = SubmitField('Upload')