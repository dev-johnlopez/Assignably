from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import StringField, FormField, SelectMultipleField, SelectField, \
                    RadioField, FieldList, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired
from app.deals.forms import ContactForm
from app.deals.models import Contact


class SettingsForm(FlaskForm):
    partnership_email_recipient = \
        SelectMultipleField('Rehab Estimate',
                            validators=[DataRequired()],
                            coerce=int)


class TenantForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired()])


class AccountForm(FlaskForm):
    email = EmailField('Login Email', validators=[DataRequired()])
    contact = FormField(ContactForm, default=lambda: Contact())
