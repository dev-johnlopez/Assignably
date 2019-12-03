from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import StringField, FormField, SelectMultipleField, SelectField, \
                    RadioField, FieldList, IntegerField
from wtforms.validators import DataRequired
from app.auth.forms import UserForm
from app.deals.models import Contact


class InvestmentLocationForm(FlaskForm):
    location_type = SelectField('Location Type',
                                choices=[('1', 'Zip Code')],
                                validators=[DataRequired()])
    location_code = StringField('Location Code', validators=[DataRequired()])

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(InvestmentLocationForm, self).__init__(csrf_enabled=csrf_enabled,
                                                     *args, **kwargs)


class InvestmentCriteriaForm(FlaskForm):
    property_type = SelectField('Property Type',
                                choices=[
                                    ('', ''),
                                    (0, 'Single Family'),
                                    (1, 'Residential Multi Family'),
                                    (2, 'Commercial Multi Fmaily'),
                                    (3, 'Self Storage'),
                                    (4, 'Retail')],
                                validators=[DataRequired()])
    flip = RadioField("Do you flip this properties?",
                      choices=[
                            ('0', 'No'),
                            ('1', 'Yes')],
                      validators=[DataRequired()])
    rental = RadioField("Do you buy & hold this properties?",
                        choices=[
                            ('0', 'No'),
                            ('1', 'Yes')],
                        validators=[DataRequired()])
    locations = FieldList(FormField(InvestmentLocationForm,
                                    default=lambda: LocationCriteria()))
    minimum_units = IntegerField()
    maximum_units = IntegerField()


class InvestorForm(FlaskForm):
    user = FormField(UserForm)
    investment_criteria = FieldList(FormField(InvestmentCriteriaForm,
                                    default=lambda: InvestmentCriteria()))
