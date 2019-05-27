from flask import Blueprint, g, render_template, redirect, url_for, g, flash
from flask_security import current_user, login_required, current_user
from app import db

bp = Blueprint('settings', __name__)

#@bp.before_app_request
#def before_request():
#    g.search_form = SearchForm()

@bp.route('/', methods=['GET', 'POST'])
@login_required
def notifications():
    deals = current_user.get_deals()
    return render_template('settings/notifications.html',
                title='Notifications',
                deals=deals)
