from flask import Blueprint, render_template, redirect, url_for
from app import db
from app.landing.forms import AddressForm
from app.deals.models import Address, Deal

bp = Blueprint('landing', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = AddressForm()
    if form.validate_on_submit():
        address = Address(
            line_1=form.street_number.data + " " + form.route.data,
            city=form.locality.data,
            state_code=form.administrative_area_level_1.data,
            postal_code=form.postal_code.data,
            country=form.country.data,
        )
        deal = Deal()
        deal.address = address
        db.session.add(deal)
        db.session.commit()
        return redirect(url_for('landing.seller', deal_id=deal.id))
    return render_template('landing/index.html', form=form)

@bp.route('/how', methods=['GET', 'POST'])
def how():
    return render_template('landing/how.html')

@bp.route('/pricing', methods=['GET', 'POST'])
def pricing():
    return render_template('landing/pricing.html')

@bp.route('/buy', methods=['GET', 'POST'])
def buy():
    return render_template('landing/buy.html')

@bp.route('/sell', methods=['GET', 'POST'])
def sell():
    return render_template('landing/sell.html')

@bp.route('/seller-lead/<deal_id>', methods=['GET', 'POST'])
def seller(deal_id):
    return render_template('landing/sell.html')
