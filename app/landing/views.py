from flask import Blueprint, render_template, redirect, url_for
from app import db
from app.landing.forms import AddressForm
from app.deals.models import Address, Deal

bp = Blueprint('landing', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('deals.index'))
    #return render_template('landing/index.html', form=form)
