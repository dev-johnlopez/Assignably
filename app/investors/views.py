from flask import Blueprint, g, render_template, redirect, url_for, g, flash, \
    request
from flask_security import current_user, login_required, current_user
from app import db
from app.email import send_email
from app.deals.forms import DealForm
from app.investors.forms import InvestorForm
from app.auth.models import User, Tenant
from app.deals.models import Deal, DealContact, DealContactRole, Contact, File

bp = Blueprint('investors', __name__)


@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
@login_required
def index(subdomain):
    investors = current_user.tenant.get_investors()
    return render_template('investors/index.html',
                           title='My Investors',
                           investors=investors)

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def new(subdomain):
    form = InvestorForm()
    criteria_data = {
        'locations': [],
    }
    form.investment_criteria.append_entry(criteria_data)
    return render_template('investors/new.html',
                           title='New Investors',
                           form=form)
