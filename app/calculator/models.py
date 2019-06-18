from app import db
from app.mixins import AuditMixin
from app.calculator import constants
from decimal import Decimal, ROUND_HALF_UP
import numpy


class Proforma(db.Model, AuditMixin):
    __tablename__ = "proforma"
    id = db.Column(db.Integer, primary_key=True)
    proforma_type = db.Column(db.Integer)
    title = db.Column(db.String(255))
    description = db.Column(db.String(5000))
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'))
    deal = db.relationship("Deal", back_populates="proformas")
    arv = db.Column(db.Integer)
    purchase_price = db.Column(db.Integer)
    seller_concessions = db.Column(db.Integer)
    closing_costs = db.Column(db.Integer)
    rehab_costs = db.Column(db.Integer)
    initial_reserve_amount = db.Column(db.Integer, default=0)
    lease_option_fee = db.Column(db.Integer)
    total_finished_sq_foot = db.Column(db.Integer)
    land_value_perc = db.Column(db.Numeric(precision=5, scale=2))
    income_tax_rate = db.Column(db.Numeric(precision=5, scale=2))
    property_appreciation_rate = db.Column(db.Numeric(precision=5, scale=2))
    vacancy_perc = db.Column(db.Numeric(precision=5, scale=2))
    sales_commission_rate = db.Column(db.Numeric(precision=5, scale=2))
    loans = db.relationship('Loan')
    income = db.relationship('LineItem',
                             foreign_keys="[LineItem.income_proforma_id]",
                             back_populates="income_proforma")
    expenses = db.relationship('LineItem',
                               foreign_keys="[LineItem.expense_proforma_id]",
                               back_populates="expense_proforma")
    capital_expenditures = db.relationship('CapitalExpenditure')

    __mapper_args__ = {
        'polymorphic_identity': 0,
        'polymorphic_on': proforma_type
    }

    def addIncomeLineItem(self, line_item):
        if self.income is None:
            self.income = []
        self.income.append(line_item)

    def addExpenseLineItem(self, line_item):
        if self.expenses is None:
            self.expenses = []
        self.expenses.append(line_item)

    def addLoan(self, loan):
        if self.loans is None:
            self.loans = []
        self.loans.append(loan)

    def addCapitalExpenditure(self, capital_expenditure):
        if self.capital_expenditures is None:
            self.capital_expenditures = []
        self.capital_expenditures.append(capital_expenditure)

    def getCapitalExpenditureAmount(self, year=None):
        capital_expenditure_amount = 0
        for capital_expenditure in self.capital_expenditures:
            capital_expenditure_amount += \
                capital_expenditure.getYearlyReserve()
        return capital_expenditure_amount

    def getInvestedCash(self):
        return self.purchase_price + self.closing_costs \
                + self.rehab_costs + self.initial_reserve_amount \
                - self.getTotalLoanAmount() - self.seller_concessions

    def getVacancyPercent(self):
        return self.vacancy_perc / 100

    def getLandValuePercent(self):
        return self.land_value_perc / 100

    def getIncomeTaxRate(self):
        return self.income_tax_rate / 100

    def getAppreciationRate(self):
        return self.property_appreciation_rate / 100

    def getTotalLoanAmount(self):
        total_loan_amount = 0
        for loan in self.loans:
            total_loan_amount += loan.amount
        return total_loan_amount

    def getDebtService(self, year=None):
        debt_service_total = 0
        for loan in self.loans:
            debt_service_total += loan.getAnnualPayment(year)
        return debt_service_total

    def getGrossScheduledIncome(self, year=None):
        income_total = 0
        for line_item in self.income:
            income_total += line_item.getAnnualizedAmount(year)
        return income_total

    def getGrossRentMultiplier(self, year=None):
        return self.purchase_price / self.getGrossScheduledIncome(year)

    def getVacancyAndCreditLoss(self, year=None):
        return self.getGrossScheduledIncome(year) * self.vacancy_perc / 100

    def getGrossOperatingIncome(self, year=None):
        return \
            elf.getGrossScheduledIncome(year) \
            - self.getVacancyAndCreditLoss(year)

    def getOperatingExpenses(self, year=None):
        expense_total = 0
        for line_item in self.expenses:
            expense_total += line_item.getAnnualizedAmount(year)
        return expense_total

    def getNetOperatingIncome(self, year=None):
        return \
            self.getGrossOperatingIncome(year) \
            - self.getOperatingExpenses(year)

    def getCapitalizationRate(self, year=None):
        # TODO - Cap Rate should be based on aquisition costs not arv.
        return self.getNetOperatingIncome(year) / self.purchase_price

    def getNetIncomeMultiplier(self, year=None):
        return 1 / self.getCapitalizationRate(year)

    def getPresentValue(self, year=None):
        return \
            self.getNetIncomeMultiplier(year) \
            * self.getNetOperatingIncome(year)

    def getDepreciationAmount(self, year=None):
        improvement_amount = self.purchase_price \
            - (self.purchase_price * self.land_value_perc/100)
        depreciation_amount = 0
        if year is None or year < 28:
            depreciation_amount = improvement_amount/Decimal(27.5)
        elif year is 28:
            depreciation_amount = improvement_amount/Decimal(27.5/2)
        # TODO when property type is available use below and remove above
        # if self.property.property_type is 4
        # or self.property.property_type is 5
        # or self.property.property_type is 6
        # or self.property.property_type is 7:
        #    depreciation_amount = improvement_amount/Decimal(39.5)
        # else:
        #     if year is None or year < 28:
        #         depreciation_amount = improvement_amount/Decimal(27.5)
        #     elif year is 28:
        #         depreciation_amount = improvement_amount/Decimal(27.5/2)
        return depreciation_amount

    def getCashflowFromDepreciation(self, year=None):
        return self.getDepreciationAmount(year) * self.income_tax_rate/100

    def getTaxableIncome(self, year=None):
        # TODO - Net Operating Income less Mortgage Interest less Depreciation,
        # Real property less Depreciation, Capital Additions less Amortization,
        # Points and Closing Costs plus Interest Earned = Taxable Income
        return self.getNetOperatingIncome(year)

    def getCashflowBeforeTaxes(self, year=None):
        # TODO - Net Operating Income less Debt Service less Capital Additions
        # plus Loan Proceeds plus Interest Earned
        return self.getNetOperatingIncome(year) - self.getDebtService(year)

    def getCashflowAfterTaxes(self, year=None):
        # TODO - figure out Tax Liability
        return self.getCashflowBeforeTaxes(year)  # - self.getTaxLiability()

    def getCashflowAfterCapEx(self, year=None):
        return \
            self.getCashflowBeforeTaxes(year) \
            - self.getCapitalExpenditureAmount(year)

    def getCashflowWithDepreciation(self, year=None):
        return \
            self.getCashflowAfterCapEx(year) \
            + self.getCashflowFromDepreciation(year)

    def getCumulativeCashflow(self, year=None):
        if year is None or year == 1:
            return self.getCashflowBeforeTaxes(1)
        else:
            return \
                self.getCashflowBeforeTaxes(year) \
                + self.getCumulativeCashflow(year-1)

    def getCashOnCashReturn(self, year=None):
        return self.getCashflowAfterTaxes(year) / self.getInvestedCash()

    def getCashOnCashReturnAfterCapex(self, year=None):
        return self.getCashflowAfterCapEx(year) / self.getInvestedCash()

    def getCashOnCashReturnIncludingDepreciation(self, year=None):
        return self.getCashflowWithDepreciation(year) / self.getInvestedCash()

    def getPricePerUnit(self):
        if self.property.units > 0:
            return self.purchase_price / self.property.units
        return "Unkown"

    def getIncomePerUnit(self, year=None):
        if self.property.units > 0:
            return self.getGrossScheduledIncome(year) / self.property.units
        return "Unkown"

    def getExpensesPerUnit(self, year=None):
        if self.property.units > 0:
            return self.getOperatingExpenses(year) / self.property.units
        return "Unkown"

    def getPricePerSquareFoot(self):
        return self.purchase_price / self.total_finished_sq_foot

    def getNetRentableAreaIncomePerSquareFoot(self, year=None):
        return self.getGrossScheduledIncome(year) / self.total_finished_sq_foot

    def getNetRentableAreaExpensesPerSquareFoot(self, year=None):
        return self.getOperatingExpenses(year) / self.total_finished_sq_foot

    def getOperatingExpenseRatio(self, year=None):
        return \
            self.getOperatingExpenses(year) \
            / self.getGrossOperatingIncome(year)

    def getDebtCoverageRatio(self, year=None):
        debt_service = self.getDebtService(year)
        if debt_service is 0:
            return "Infinite"
        return self.getNetOperatingIncome(year) / self.getDebtService(year)

    def getBreakEvenRatio(self, year=None):
        return \
            (self.getDebtService(year) + self.getOperatingExpenses(year)) \
            / self.getGrossOperatingIncome(year)

    def getReturnOnEquity(self, year=None):
        return self.getCashflowAfterTaxes(year) / self.getInvestedCash()

    def getSalePrice(self, year=None):
        if year > 0:
            return self.arv \
                * (1 + (self.property_appreciation_rate/100))**(year)
        return self.arv

    def getSalesCosts(self, year=None):
        return self.getSalePrice(year) * self.sales_commission_rate/100

    def getTotalProfit(self, year=None):
        income = self.getSalePrice(year) + self.getCumulativeCashflow(year)
        expenses = self.getInvestedCash() + self.lease_option_fee \
            + self.getSalesCosts(year)
        for loan in self.loans:
            expenses += loan.getLoanBalance(year)
        return income - expenses

    def getReturnOnInvestment(self, year=None):
        return self.getTotalProfit(year) / self.getInvestedCash()

    def getAnnualizedROI(self, year=None):
        if year is None or year == 0:
            year = 1
        return self.getReturnOnInvestment(year) / year

    def getCompoundROI(self, year=None):
        numerator = self.getTotalProfit(year) + self.getInvestedCash()
        denominator = self.getInvestedCash()
        return (((numerator/denominator)**(1/year)) - 1)

    def getIRR(self, year=None):
        irr_list = []
        irr_list.append(-1*self.getInvestedCash())
        period = 0
        while period < year:
            if period + 1 == year:
                total_withdrawal = self.getInvestedCash() \
                    + self.getTotalProfit(year)
                if year > 1:
                    total_withdrawal -= self.getCumulativeCashflow(year - 1)
                irr_list.append(total_withdrawal)
            else:
                irr_list.append(self.getCashflowBeforeTaxes(period + 1))
            period += 1
        return round(numpy.irr(irr_list), 5)

    def getEquity(self, year=None):
        if self.loans is not None:
            return self.arv - sum(loan.getLoanBalance(year)
                                  for loan in self.loans)
        else:
            return self.arv

    # TODO - Cashflow calculations Chapter #32 and onward.
    # http://www.wikisummaries.org/wiki/What_Every_Real_Estate_Investor_Needs_to_Know_about_Cash_Flow..._And_36_Other_Key_Financial_Measures#Chapter_6:_Calculation_1:_Simple_Interest


class Loan(db.Model, AuditMixin):
    __tablename__ = "loan"
    id = db.Column(db.Integer, primary_key=True)
    proforma_id = db.Column(db.Integer, db.ForeignKey('proforma.id'))
    type = db.Column(db.Integer)
    amount = db.Column(db.Integer, default=0)
    interest_rate = db.Column(db.Numeric(precision=6, scale=3))
    interest_only = db.Column(db.Boolean)
    length = db.Column(db.Integer)

    def getType(self):
        return constants.LOAN_TYPE[self.type]

    def getInterestRate(self):
        return self.interest_rate/100

    def getLoanBalance(self, year=None):
        if self.interest_only:
            return self.amount
        pv = self.amount
        pmt = self.getMonthlyPayment()
        i = self.interest_rate/100 / 12
        n = 0
        if year is not None:
            n = year*12
        return pv*(1 + (i))**n - pmt * (((1+i)**n - 1)/i)

    def getDiscountFactor(self):
        rate_per_period = Decimal(self.interest_rate) / Decimal(100) / 12
        number_of_periods = Decimal(self.length*12)
        return (((1 + rate_per_period)**number_of_periods) - 1) \
            / (rate_per_period*(1+rate_per_period)**number_of_periods)

    def getMonthlyPayment(self):
        payment = 0
        present_value = Decimal(self.amount)
        if self.interest_only:
            payment = present_value * self.getInterestRate() / 12
        else:
            payment = present_value / self.getDiscountFactor()
        cents = Decimal('.01')
        money = payment.quantize(cents, ROUND_HALF_UP)
        return money

    def getAnnualPayment(self, year=None):
        if year is not None and year > self.length:
            return 0
        return self.getMonthlyPayment() * 12


class LineItem(db.Model, AuditMixin):
    __tablename__ = "line_item"
    id = db.Column(db.Integer, primary_key=True)
    income_proforma_id = db.Column(db.Integer, db.ForeignKey('proforma.id'))
    income_proforma = db.relationship("Proforma",
                                      back_populates='income',
                                      foreign_keys="[LineItem\
                                                    .income_proforma_id]")
    expense_proforma_id = db.Column(db.Integer, db.ForeignKey('proforma.id'))
    expense_proforma = db.relationship("Proforma",
                                       back_populates='expenses',
                                       foreign_keys="[LineItem\
                                                    .expense_proforma_id]")
    type = db.Column(db.String(255))
    amount = db.Column(db.Integer, default=0)
    amount_type = db.Column(db.String(50))
    frequency = db.Column(db.Integer)
    annual_increase_perc = db.Column(db.Numeric(precision=6, scale=2))

    def getFrequency(self):
        return constants.FREQUENCY_TYPE[self.frequency]

    def getAmount(self):
        return self.amount

    def getAnnualizedAmount(self, year=None):
        principal = self.getAmount() * self.frequency
        if year is None:
            return principal
        rate = 0
        if self.getAnnualIncreasePerc() is not None:
            rate = self.getAnnualIncreasePerc()
        return principal * (1 + rate)**(year - 1)

    def getAnnualIncreasePerc(self):
        return self.annual_increase_perc / 100

    def getProforma(self):
        if self.income_proforma is not None:
            return self.income_proforma
        else:
            return self.expense_proforma

    __mapper_args__ = {
        'polymorphic_identity': 'Fixed',
        'polymorphic_on': amount_type
    }


class PercentLineItem(LineItem):
    calculation = db.Column(db.String(255))

    __mapper_args__ = {
        'polymorphic_identity': 'Percent'
    }

    def getAnnualizedAmount(self, year=None):
        return self.getAmount(year) * self.frequency

    def getAmount(self, year=None):
        return \
            self.amount \
            * self.getProforma().getGrossScheduledIncome(year) / 100

    def getAnnualIncreasePerc(self):
        return "N/a"

    def __init__(self, **kwargs):
        super(PercentLineItem, self).__init__(**kwargs)


class CapitalExpenditure(db.Model, AuditMixin):
    __tablename__ = "capital_expenditure"
    id = db.Column(db.Integer, primary_key=True)
    proforma_id = db.Column(db.Integer, db.ForeignKey('proforma.id'))
    type = db.Column(db.String(255))
    replacement_cost = db.Column(db.Numeric(precision=12, scale=2))
    lifespan = db.Column(db.Integer)

    def getYearlyReserve(self):
        return self.replacement_cost / self.lifespan

    def getMonthlyReserve(self):
        return self.getYearlyReserve() / 12
