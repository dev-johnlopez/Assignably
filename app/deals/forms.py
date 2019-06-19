from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FormField, BooleanField, \
                    TextAreaField, SelectField, FieldList, HiddenField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, url, Optional
from app.deals.models import Address, File, DealContact, DealContactRole, \
                             Contact


class AddressForm(FlaskForm):
    line_1 = StringField('Street Address', validators=[])
    line_2 = StringField('Unit / Apt', validators=[])
    city = StringField('City', validators=[])
    state_code = SelectField('State', choices=[
        ('', ''),
        ('AK', 'Alaska'),
        ('AL', 'Alabama'),
        ('AR', 'Arkansas'),
        ('AZ', 'Arizona'),
        ('CA', 'California'),
        ('CT', 'Connecticut'),
        ('DC', 'Washington DC'),
        ('DE', 'Delaware'),
        ('FL', 'Florida'),
        ('GA', 'Georgia'),
        ('HI', 'Hawaii'),
        ('IA', 'Iowa'),
        ('ID', 'Idaho'),
        ('IL', 'Illinois'),
        ('IN', 'Indiana'),
        ('KS', 'Kansas'),
        ('KY', 'Kentucky'),
        ('LA', 'Louisiana'),
        ('MA', 'Massachusetts'),
        ('MA', 'Massachusetts'),
        ('MD', 'Maryland'),
        ('ME', 'Maine'),
        ('MI', 'Michigan'),
        ('MN', 'Minnesota'),
        ('MO', 'Missouri'),
        ('MS', 'Mississippi'),
        ('MT', 'Montana'),
        ('NC', 'North Carolina'),
        ('ND', 'North Dakota'),
        ('NE', 'Nebraska'),
        ('NH', 'New Hampshire'),
        ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'),
        ('NV', 'Nevada'),
        ('NY', 'New York'),
        ('OH', 'Ohio'),
        ('OK', 'Oklahoma'),
        ('OR', 'Oregon'),
        ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'),
        ('SD', 'South Dakota'),
        ('TN', 'Tennessee'),
        ('TX', 'Texas'),
        ('UT', 'Utah'),
        ('VA', 'Virginia'),
        ('VT', 'Vermont'),
        ('WA', 'Washington'),
        ('WI', 'Wisconsin'),
        ('WV', 'West Virginia'),
        ('WY', 'Wyoming')
    ], validators=[])
    postal_code = StringField('ZIP Code', validators=[])


class FileForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    file_type = HiddenField('Type', validators=[Optional()])
    url = URLField(validators=[DataRequired(), url()])

    def __init__(self, csrf_enabled=False, *args, **kwargs):
        super(FileForm, self).__init__(csrf_enabled=csrf_enabled,
                                       *args,
                                       **kwargs)


class DealContactRoleForm(FlaskForm):
    name = StringField('Name', validators=[Optional()])


class ContactForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])


class DealContactForm(FlaskForm):
    contact = FormField(ContactForm, default=lambda: Contact())
    roles = FieldList(FormField(DealContactRoleForm,
                      default=lambda:
                      DealContactRole()))


class DealForm(FlaskForm):
    address = FormField(AddressForm, default=lambda: Address())
    contacts = FieldList(FormField(DealContactForm,
                                   default=lambda: DealContact()))
    files = FieldList(FormField(FileForm, default=lambda: File()))
    rehab_estimate = IntegerField('Rehab Estimate', validators=[Optional()])
    sq_feet = IntegerField('Sq. Feet', validators=[Optional()])
    bedrooms = IntegerField('Bedrooms', validators=[Optional()])
    bathrooms = IntegerField('Bathrooms', validators=[Optional()])
    after_repair_value = IntegerField('ARV', validators=[Optional()])
    purchase_price = IntegerField('Purchase Price', validators=[Optional()])
    list_price = IntegerField('List Price', validators=[Optional()])
    property_tax = IntegerField('Property Tax', validators=[Optional()])
    under_contract_ind = SelectField('Under Contract?',
                                     choices=[
                                            ('', ''),
                                            ('1', 'Yes'),
                                            ('0', 'No')],
                                     validators=[DataRequired()])
