from flask import Blueprint, g, render_template, redirect, url_for, g, flash, \
    request, current_app, after_this_request
from flask_security import current_user, login_required, current_user, SQLAlchemyUserDatastore
from flask_security.registerable import register_user
from flask_security.utils import login_user, get_post_register_redirect
from app import db, security
from app.auth.models import User, Company, Role
from app.auth.forms import ExtendedRegisterForm
from app.deals.models import Contact
from werkzeug.local import LocalProxy

bp = Blueprint('auth', __name__)

# Convenient references
_security = LocalProxy(lambda: current_app.extensions['security'])
_datastore = LocalProxy(lambda: _security.datastore)


def _commit(response=None):
    _datastore.commit()
    return response


def _ctx(endpoint):
    return _security._run_ctx_processor(endpoint)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if _security.confirmable or request.is_json:
        form_class = _security.confirm_register_form
    else:
        form_class = _security.register_form

    if request.is_json:
        form_data = MultiDict(request.get_json())
    else:
        form_data = request.form

    form = form_class(form_data)

    if form.validate_on_submit():
        user_data = {
            'email': form.email.data,
            'password': form.password.data
        }
        user = register_user(**user_data)
        contact = Contact(first_name=form.contact.first_name.data,
                          last_name=form.contact.last_name.data,
                          email=form.email.data,
                          phone=form.contact.phone.data)
        company = Company(name=form.company.company_name.data)
        company.add_user(user)
        company.get_settings().partnership_email_recipient = user.email
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        role = user_datastore.find_or_create_role("Company Admin")
        user_datastore.add_role_to_user(user, role)
        user.company = company
        user.contact = contact
        form.user = user

        if not _security.confirmable or _security.login_without_confirmation:
            after_this_request(_commit)
            login_user(user)

        if not request.is_json:
            if 'next' in form:
                redirect_url = get_post_register_redirect(form.next.data)
            else:
                redirect_url = get_post_register_redirect()

            return redirect(redirect_url)
        return _render_json(form, include_auth_token=True)

    if request.is_json:
        return _render_json(form)

    return _security.render_template('/security/register_user.html',
                                     register_user_form=form,
                                     **_ctx('register'))
