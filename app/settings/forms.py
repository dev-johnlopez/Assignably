from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

class SettingsForm(FlaskForm):
    partnership_email_recipient = EmailField('Rehab Estimate', validators=[DataRequired()])
