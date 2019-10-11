from flask import Blueprint, g, render_template, redirect, url_for, g, flash
from flask_security import current_user, login_required, current_user
from app import db
from .forms import SettingsForm, CompanyForm, AccountForm
from flask_security.registerable import register_user
from app.deals.forms import ContactForm
from app.deals.models import Contact
from app.auth.models import User
import random
import string

bp = Blueprint('settings', __name__)


@bp.route('/', methods=['GET', 'POST'])
@login_required
def notifications():
    form = SettingsForm()
    user_list=[(user.id, user) for user in current_user.company.users]
    #passing group_list to the form
    form.partnership_email_recipient.choices = user_list
    if form.validate_on_submit():
        flash('You\'re info has been saved.', 'info')
        form.populate_obj(current_user.company.get_settings())
        db.session.add(current_user.company.get_settings())
        db.session.commit()
    return render_template('settings/notifications.html',
                           title='Settings',
                           form=form)


@bp.route('/company', methods=['GET', 'POST'])
@login_required
def company():
    form = CompanyForm(obj=current_user.company)
    if form.validate_on_submit():
        flash('You\'re info has been saved.', 'info')
        form.populate_obj(current_user.company)
        db.session.add(current_user.company)
        db.session.commit()
    return render_template('settings/company.html',
                           title='My Company',
                           form=form)


@bp.route('/new-user', methods=['GET', 'POST'])
@login_required
def new_user():
    form = ContactForm()
    if form.validate_on_submit():
        user_data = {
            'email': form.email.data,
            'password':
                ''.join(
                    [random.choice(string.ascii_letters + string.digits)
                        for n in xrange(64)])
        }
        user = register_user(**user_data)
        print("registered user")
        contact = Contact(first_name=form.first_name.data,
                          last_name=form.last_name.data,
                          email=form.email.data,
                          phone=form.phone.data)
        user.contact = contact
        user.company = current_user.company
        db.session.add(contact)
        db.session.add(user)
        db.session.add(current_user.company)
        db.session.commit()
        return redirect(url_for('.company'))
    flash(form.errors, 'info')
    return render_template('settings/new-user.html',
                           title="New User",
                           form=form)

@bp.route('<user_id>/edit-user', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = ContactForm(obj=user.contact)
    if form.validate_on_submit():
        form.populate_obj(user.contact)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('.company'))
    flash(form.errors, 'info')
    return render_template('settings/new-user.html',
                           title="New User",
                           form=form)


@bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = AccountForm(obj=current_user)
    if form.validate_on_submit():
        flash('You\'re info has been saved.', 'info')
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
    return render_template('settings/my-account.html',
                           title='My Account',
                           form=form)
