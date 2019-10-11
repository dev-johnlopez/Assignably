from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FormField, BooleanField, \
                    TextAreaField, SelectField, FieldList, HiddenField
from flask_security.forms import RegisterForm
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Optional


class ContactForm(FlaskForm):
    first_name = StringField('First Name', [Optional()])
    last_name = StringField('Last Name', [Optional()])
    phone = StringField('Last Name', [Optional()])


class RoleForm(FlaskForm):
    role_type = QuerySelectField(
        'Role Type',
        query_factory=lambda: models.Role.query,
        allow_blank=False
    )


class CompanyForm(FlaskForm):
    company_name = StringField('Company Name', [DataRequired()])


class ExtendedRegisterForm(RegisterForm):
    company = FormField(CompanyForm)
    contact = FormField(ContactForm)


class UserForm(FlaskForm):
    contact = FormField(ContactForm)
