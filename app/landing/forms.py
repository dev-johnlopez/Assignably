from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FormField, BooleanField, \
                    TextAreaField, SelectField, FieldList, HiddenField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, url, Optional
from app.deals.models import Address, File, DealContact, DealContactRole, \
                             Contact


class AddressForm(FlaskForm):
    street_number = StringField("Street Number", validators=[DataRequired()])
    route = StringField("Street", validators=[DataRequired()])
    locality = StringField("City", validators=[DataRequired()])
    administrative_area_level_1 = StringField("City", validators=[DataRequired()])
    postal_code = StringField("Zip Code", validators=[DataRequired()])
    country = StringField("Country", validators=[DataRequired()])


class DealForm(FlaskForm):
    address = FormField(AddressForm, default=lambda: Address())
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
                                            (True, 'Yes'),
                                            (False, 'No')],
                                     validators=[DataRequired()],
                                     coerce=lambda x: x == 'True')
