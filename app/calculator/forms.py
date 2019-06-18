from flask_wtf import FlaskForm
from wtforms import IntegerField, DecimalField, FormField, FieldList, \
    BooleanField, SelectField, StringField, HiddenField
from wtforms.validators import DataRequired, Optional
from app.calculator import constants


class LoanForm(FlaskForm):
    type = SelectField('Loan Type',
                       description='The type of loan \
                                used to purchase the property.',
                       choices=[
                            ('', ''),
                            (str(constants.CONVENTIONAL),
                                'Conventional'),
                            (str(constants.HARD_MONEY), 'Hard Money'),
                            (str(constants.PRIVATE_MONEY),
                                'Private Money'),
                            (str(constants.OTHER), 'Other')
                       ],
                       validators=[DataRequired()])
    amount = IntegerField('Loan Amount',
                          description='The amount of this this loan.',
                          validators=[DataRequired()])
    interest_rate = DecimalField('Interest Rate',
                                 description='The interest rate of the loan.',
                                 validators=[DataRequired()])
    interest_only = BooleanField('Interest Only?',
                                 description='Mark Yes if this is an interest \
                                 only loan.',
                                 validators=[Optional()])
    length = IntegerField('Length of Loan',
                          description='The length (in years) for this loan.',
                          validators=[DataRequired()])


class LineItemForm(FlaskForm):
    type = StringField('Description',
                       description='A description of the line item.',
                       validators=[DataRequired()])
    amount = IntegerField('Amount',
                          description='The amount for this line item \
                          (always input positive values).',
                          validators=[DataRequired()])
    amount_type = HiddenField('Amount Type',
                              description='Determines if this is a Fixed or \
                              Percentage-based line item.',
                              validators=[DataRequired()],
                              default="Fixed")
    frequency = SelectField('Frequency',
                            choices=[
                                ('', ''),
                                (str(constants.MONTHLY),
                                    'Monthly'),
                                (str(constants.ANNUALLY),
                                    'Annually')
                            ],
                            validators=[DataRequired()])
    annual_increase_perc = DecimalField('Annual Increase Rate',
                                        description='Annual expected \
                                        increase.',
                                        validators=[Optional()])
    calculation = SelectField('Calculated From',
                              choices=[
                                ('', ''),
                                ('GOI', 'GOI')],
                              validators=[Optional()])


class CapitalExpenditureForm(FlaskForm):
    type = StringField('Description',
                       description='A description of the capital expenditure.',
                       validators=[DataRequired()])
    replacement_cost = IntegerField('Replacement Cost',
                                    description='How much it costs for \
                                    this expenditure.',
                                    validators=[DataRequired()])
    lifespan = IntegerField('Lifespan',
                            description='The length in years until this \
                            expense occurs.',
                            validators=[DataRequired()])


class ProformaForm(FlaskForm):
    title = StringField('Title',
                        description='The title of this proforma.',
                        validators=[DataRequired()])
    description = StringField('Description',
                              description='Details of this proforma.',
                              validators=[Optional()])
    arv = IntegerField('ARV',
                       description='The ARV for must purchases is the \
                       Purchase Price. If you are buying at a discount and \
                       the property is worth more enter the higher value \
                       here. For example, if you are buying a $200k house \
                       at $190k then you would enter 200000 in this field \
                       and 190000 in the Purchase Price field.',
                       validators=[DataRequired()])
    purchase_price = IntegerField('Purchase Price',
                                  description='The price paid to purchase \
                                  the property.',
                                  validators=[DataRequired()])
    seller_concessions = IntegerField('Seller Concessions',
                                      description='Credit given to the buyer \
                                      at closing by the seller.',
                                      validators=[Optional()])
    closing_costs = IntegerField('Closing Costs',
                                 description='Typical closing costs are 1-2%% \
                                 of the purchase but can vary widely. This \
                                 field should include ALL closing costs from \
                                 the first and second loan (if applicable).',
                                 validators=[DataRequired()])
    rent_ready_costs = IntegerField('Rent Ready Costs',
                                    description='Initial costs to get the \
                                    property ready to rent. This may include \
                                    upcoming large expenses for which the \
                                    maintenance account will not be able to \
                                    handle such as roof, furnace, A/C, etc.',
                                    validators=[Optional()])
    initial_reserve_amount = IntegerField('Initial Reserve Amount',
                                          description='The Initial Reserves \
                                          planned to set aside for this \
                                          property. This can be very \
                                          important to have in a deal being \
                                          done in a partnership.',
                                          validators=[Optional()])
    lease_option_fee = IntegerField('Lease Option Fee',
                                    description='The Lease Option Fee is an \
                                    up front fee paid by a tenant buyer. The \
                                    fee is typically non-refundable and is \
                                    usually applied towards their down \
                                    payment or purchase price if they \
                                    purchase the house. (This calculator \
                                    applies it to the down payment if they \
                                    purchase the property.)',
                                    validators=[Optional()])
    total_finished_sq_foot = IntegerField('Total Finished Square Footage',
                                          description='The total square \
                                          footage area. Used to calculate \
                                          the operating efficiency rate.',
                                          validators=[Optional()])
    land_value_perc = DecimalField('Land Value Percent',
                                   description='The value of the land of the \
                                   property being purchased. This is used to \
                                   calculate depreciation as depreciation can \
                                   only be taken on the improvements \
                                   (buildings) and not on the land.',
                                   validators=[Optional()])
    income_tax_rate = DecimalField('Effective Income Tax Rate',
                                   description='The buyer\'s effective \
                                   tax rate.',
                                   validators=[Optional()])

    vacancy_perc = DecimalField('Vacancy Rate',
                                description='Percent of time the property is \
                                expected to be vacant. the type of property \
                                and location will determine this to some \
                                extent but typical vacancy is 5-10%%. There \
                                are many ways to lower vacancy (including \
                                lowering rent). 3%% is the lowest you should \
                                probably ever use and that\'s only as an \
                                experienced landlord. When in doubt, \
                                be conservative and use a higher vacancy.',
                                validators=[Optional()])
    property_appreciation_rate = DecimalField('Appreciation Rate',
                                              description='The percentage in \
                                              which this property will \
                                              appreciate year over year.',
                                              validators=[Optional()])
    sales_commission_rate = DecimalField('Sales Commission Rate',
                                         description='The anticipate \
                                         commission rate paid when selling \
                                         the property.',
                                         validators=[Optional()])
    loans = FieldList(FormField(LoanForm))
    income = FieldList(FormField(LineItemForm))
    expenses = FieldList(FormField(LineItemForm))
    capital_expenditures = FieldList(FormField(CapitalExpenditureForm))
