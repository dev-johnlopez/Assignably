from flask import g, render_template, flash, redirect, url_for, request, \
    Blueprint
from app import db
# from app.forms.search import SearchForm
from flask_security import current_user
from app.deals.models import Deal
from app.calculator.models import Proforma, LineItem
from app.calculator.forms import ProformaForm, LineItemForm
import locale

bp = Blueprint('calculator', __name__)


# @bp.before_app_request
# def before_request():
#     g.search_form = SearchForm()


@bp.route('/<proforma_id>')
def view(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    form = ProformaForm(obj=proforma)
    return render_template('proformas/view.html',
                           title="View",
                           proforma=proforma,
                           form=form)


@bp.route('/<proforma_id>/details')
def details(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    form = ProformaForm(obj=proforma)
    return render_template('proformas/details.html',
                           title="Details",
                           proforma=proforma,
                           form=form)


@bp.route('/<proforma_id>/calculations')
def calculations(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    return render_template('proformas/calculations.html',
                           title="Calculations",
                           proforma=proforma)


@bp.route('/add/<deal_id>', methods=['GET', 'POST'])
def create(deal_id):
    deal = Deal.query.get(deal_id)
    form = ProformaForm()
    if form.validate_on_submit():
        proforma = Proforma()
        form.populate_obj(proforma)
        deal.addProforma(proforma)
        db.session.add(deal)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    return render_template('calculator/wizard.html',
                           title="Add Proforma",
                           deal=deal,
                           form=form)


@bp.route('/edit/<proforma_id>', methods=['GET', 'POST'])
def edit(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    form = ProformaForm(obj=proforma)
    if form.validate_on_submit():
        income = proforma.income
        expenses = proforma.expenses
        capital_expenditures = proforma.capital_expenditures
        loans = proforma.loans
        form.populate_obj(proforma)
        proforma.income = income
        proforma.expenses = expenses
        proforma.capital_expenditures = capital_expenditures
        proforma.loans = loans
        db.session.add(proforma)
        db.session.commit()
        return redirect(url_for('.details', proforma_id=proforma.id))
    return render_template('proformas/create.html',
                           title="Edit Proforma",
                           deal=deal,
                           form=form)


@bp.route('/delete/<proforma_id>', methods=['GET', 'POST'])
def delete(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    deal = proforma.deal
    db.session.delete(proforma)
    db.session.commit()
    return redirect(url_for('deals.view', deal_id=deal.id))


@bp.route('<proforma_id>/add/income', methods=['GET', 'POST'])
def add_income(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    form = LineItemForm()
    if form.validate_on_submit():
        line_item = LineItem()
        form.populate_obj(line_item)
        proforma.addIncomeLineItem(line_item)
        db.session.add(proforma)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    return render_template('proformas/line_item.html',
                           title="Add Proforma",
                           line_item_type="Income",
                           proforma=proforma,
                           form=form)


@bp.route('edit/income/<line_item_id>', methods=['GET', 'POST'])
def edit_income(line_item_id):
    line_item = LineItem.query.get(line_item_id)
    proforma = Proforma.query.get(line_item.income_proforma_id)
    form = LineItemForm(obj=line_item)
    if form.validate_on_submit():
        form.populate_obj(line_item)
        db.session.add(line_item)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    return render_template('proformas/line_item.html',
                           title="Edit Proforma",
                           line_item_type="Income",
                           proforma=proforma,
                           form=form)


@bp.route('<proforma_id>/add/fixed_expense', methods=['GET', 'POST'])
def add_fixed_expense(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    form = LineItemForm()
    form.amount_type.data = 'Fixed'
    if form.validate_on_submit():
        line_item = LineItem()
        form.populate_obj(line_item)
        proforma.addExpenseLineItem(line_item)
        db.session.add(proforma)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    return render_template('proformas/line_item.html',
                           title="Add Proforma",
                           line_item_type="Expense",
                           proforma=proforma,
                           form=form)


@bp.route('<proforma_id>/add/percent_expense', methods=['GET', 'POST'])
def add_percent_expense(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    form = LineItemForm()
    form.amount_type.data = 'Percent'
    form.frequency.data = '1'
    if form.validate_on_submit():
        line_item = PercentLineItem()
        form.populate_obj(line_item)
        proforma.addExpenseLineItem(line_item)
        db.session.add(proforma)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    for error in form.errors:
        flash(error, 'info')
    return render_template('proformas/line_item.html',
                           title="Add Proforma",
                           line_item_type="Expense",
                           proforma=proforma,
                           form=form)


@bp.route('edit/expense/<line_item_id>', methods=['GET', 'POST'])
def edit_expense(line_item_id):
    line_item = LineItem.query.get(line_item_id)
    proforma = Proforma.query.get(line_item.expense_proforma_id)
    form = LineItemForm(obj=line_item)
    if form.validate_on_submit():
        form.populate_obj(line_item)
        db.session.add(line_item)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    return render_template('proformas/line_item.html',
                           title="Edit Expense",
                           line_item_type="Expense",
                           proforma=proforma,
                           form=form)


@bp.route('/delete/line_item/<line_item_id>', methods=['GET', 'POST'])
def delete_line_item(line_item_id):
    line_item = LineItem.query.get(line_item_id)
    db.session.delete(line_item)
    db.session.commit()
    return redirect(url_for('proformas.details', proforma_id=proforma_id))


@bp.route('<proforma_id>/add/loan', methods=['GET', 'POST'])
def add_loan(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    form = LoanForm()
    if form.validate_on_submit():
        loan = Loan()
        form.populate_obj(loan)
        proforma.addLoan(loan)
        db.session.add(proforma)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    return render_template('proformas/financing.html',
                           title="Add Loan",
                           proforma=proforma,
                           form=form)


@bp.route('edit/loan/<loan_id>', methods=['GET', 'POST'])
def edit_loan(loan_id):
    loan = Loan.query.get(loan_id)
    proforma = Proforma.query.get(loan.proforma_id)
    form = LoanForm(obj=loan)
    if form.validate_on_submit():
        form.populate_obj(loan)
        db.session.add(loan)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    return render_template('proformas/financing.html',
                           title="Edit Loan",
                           proforma=proforma,
                           form=form)


@bp.route('/delete/loan/<loan_id>', methods=['GET', 'POST'])
def delete_loan(loan_id):
    loan = Loan.query.get(loan_id)
    proforma = Proforma.query.get(loan.proforma_id)
    db.session.delete(loan)
    db.session.commit()
    return redirect(url_for('proformas.details', proforma_id=proforma.id))


@bp.route('<proforma_id>/add/captial_expenditure', methods=['GET', 'POST'])
def add_capital_expenditure(proforma_id):
    proforma = Proforma.query.get(proforma_id)
    form = CapitalExpenditureForm()
    if form.validate_on_submit():
        capital_expenditure = CapitalExpenditure()
        form.populate_obj(capital_expenditure)
        proforma.addCapitalExpenditure(capital_expenditure)
        db.session.add(proforma)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    return render_template('proformas/capital_expenditure.html',
                           title="Add Capital Expenditure",
                           proforma=proforma,
                           form=form)


@bp.route('edit/capital_expenditure/<capital_expenditure_id>',
          methods=['GET', 'POST'])
def edit_capital_expenditure(capital_expenditure_id):
    capital_expenditure = CapitalExpenditure.query.get(capital_expenditure_id)
    proforma = Proforma.query.get(capital_expenditure.proforma_id)
    form = CapitalExpenditureForm(obj=capital_expenditure)
    if form.validate_on_submit():
        form.populate_obj(capital_expenditure)
        db.session.add(capital_expenditure)
        db.session.commit()
        return redirect(url_for('proformas.details', proforma_id=proforma.id))
    return render_template('proformas/capital_expenditure.html',
                           title="Edit Captial Expenditure",
                           proforma=proforma,
                           form=form)


@bp.route('/delete/capital_expenditure/<capital_expenditure_id>',
          methods=['GET', 'POST'])
def delete_capital_expenditure(capital_expenditure_id):
    capital_expenditure = CapitalExpenditure.query.get(capital_expenditure_id)
    proforma = Proforma.query.get(capital_expenditure.proforma_id)
    db.session.delete(capital_expenditure)
    db.session.commit()
    return redirect(url_for('proformas.details', proforma_id=proforma.id))


@bp.app_template_filter()
def currency(value):
    if value is None:
        return "$0.00"
    return locale.currency(value, grouping=True)


@bp.app_template_filter()
def percent(value):
    if value is None:
        return "0.00%"
    if not isinstance(value, float) and not isinstance(value, Decimal):
        return value
    return "{}%".format(round(value*100, 2))
