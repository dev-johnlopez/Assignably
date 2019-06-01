from flask import Blueprint, g, render_template, redirect, url_for, g, flash
from flask_security import current_user, login_required, current_user
from app import db
from .forms import SettingsForm

bp = Blueprint('settings', __name__)


@bp.route('/', methods=['GET', 'POST'])
@login_required
def notifications():
    form = SettingsForm(obj=current_user.getSettings())
    if form.validate_on_submit():
        flash('You\'re info has been saved.', 'info')
        form.populate_obj(current_user.getSettings())
        db.session.add(current_user.getSettings())
        db.session.commit()
    return render_template('settings/notifications.html',
                           title='Notifications',
                           form=form)
