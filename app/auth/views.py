# -*- coding: utf-8 -*-
"""
    flask_security.views
    ~~~~~~~~~~~~~~~~~~~~

    Flask-Security views module

    :copyright: (c) 2012 by Matt Wright.
    :license: MIT, see LICENSE for more details.
"""
import random, string
from flask import Blueprint, after_this_request, current_app, jsonify, \
    redirect, request, url_for
from flask_login import current_user
from werkzeug.datastructures import MultiDict
from werkzeug.local import LocalProxy
from sqlalchemy import func
from flask_security.changeable import change_user_password
from flask_security.confirmable import confirm_email_token_status, confirm_user, \
    send_confirmation_instructions
from flask_security.decorators import anonymous_user_required, login_required
from flask_security.passwordless import login_token_status, send_login_instructions
from flask_security.recoverable import reset_password_token_status, \
    send_reset_password_instructions, update_password
from flask_security.utils import config_value, do_flash, get_message, \
    get_post_login_redirect, get_post_logout_redirect, \
    get_post_register_redirect, get_url, login_user, logout_user, \
    slash_url_suffix, hash_password
from flask_security.signals import login_instructions_sent, \
    reset_password_instructions_sent, user_registered
from app import db
from app.decorators import tenant_required
from app.auth.models import Tenant, User
from app.auth.forms import TenantRegisterForm, EmailForm, TenantSelectForm, \
    LoginForm

bp = Blueprint('security', __name__)

# Convenient references
_security = LocalProxy(lambda: current_app.extensions['security'])

_datastore = LocalProxy(lambda: _security.datastore)


def _render_json(form, include_user=True, include_auth_token=False):
    has_errors = len(form.errors) > 0

    if has_errors:
        code = 400
        response = dict(errors=form.errors)
    else:
        code = 200
        response = dict()
        if include_user:
            response['user'] = form.user.get_security_payload()

        if include_auth_token:
            token = form.user.get_auth_token()
            response['user']['authentication_token'] = token

    return jsonify(dict(meta=dict(code=code), response=response)), code


def _commit(response=None):
    _datastore.commit()
    return response


def _ctx(endpoint):
    return _security._run_ctx_processor(endpoint)


@bp.route('/login', methods=['GET'])
@anonymous_user_required
def login():
    """View function for login view"""

    form = EmailForm(request.form)
    email = request.args.get('email')
    if email is not None:
        return redirect(url_for('security.select_account', email=email))

    if request.is_json:
        return _render_json(form, include_auth_token=True)

    return _security.render_template('security/login_tenant.html',
                                     login_user_form=form,
                                     **_ctx('login'))

@bp.route('/account', methods=['GET', 'POST'])
@anonymous_user_required
def select_account():
    """View function for login view"""
    email = request.args.get('email')
    tenant_form = TenantSelectForm(request.form)
    tenant_form.organization.query_factory = lambda: Tenant.query.join(User).filter(func.lower(User.email) == func.lower(email))
    tenant_form.email.data = email
    organization = request.args.get('organization')
    if email is not None and organization is not None:
        tenant = Tenant.query.get(organization)
        print("redirecting to" + url_for('security.login', subdomain=tenant.subdomain, email=email))
        return redirect(url_for('security.user_login', subdomain=tenant.subdomain, email=email))

    if tenant_form.validate_on_submit():
        login_user(form.user, remember=form.remember.data)
        after_this_request(_commit)

        if not request.is_json:
            return redirect(get_post_login_redirect(form.next.data))

    if request.is_json:
        return _render_json(form, include_auth_token=True)

    return _security.render_template('security/select_account.html',
                                     tenant_form=tenant_form,
                                     email=email,
                                     **_ctx('login'))


@bp.route('/u/login', methods=['GET', 'POST'], subdomain="<subdomain>")
def user_login(subdomain):
    """View function for login view"""
    print("looking for tenant " + subdomain)
    tenant = Tenant.query.filter(func.lower(Tenant.subdomain) == func.lower(subdomain)).first()
    if tenant is None:
        print("tenant was not found...")
        return redirect(url_for('security.login'))

    form = LoginForm()
    tenant_name = tenant.name
    email = request.args.get('email')

    if(email is not None):
        form.email.data = email

    print("**123***")
    if form.validate_on_submit():
        print("*******")
        print("*******")
        print("*******")
        print(form.user)
        login_user(form.user, remember=form.remember.data)
        after_this_request(_commit)

        if not request.is_json:
            return redirect(url_for('deals.index', subdomain=subdomain))

    if request.is_json:
        return _render_json(form, include_auth_token=True)

    form.subdomain = subdomain
    return _security.render_template(config_value('LOGIN_USER_TEMPLATE'),
                                     login_user_form=form,
                                     tenant_name=tenant_name,
                                     subdomain=subdomain,
                                     **_ctx('login'))

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """View function which handles a logout request."""
    print("trying to logout...")
    if current_user.is_authenticated:
        print("logging out")
        logout_user()

    return redirect(url_for('security.login'))

@bp.route('/register', methods=['GET', 'POST'])
@anonymous_user_required
def tenant_register():
    """View function which handles a registration request."""
    print("in tenant register")
    if request.is_json:
        form_data = MultiDict(request.get_json())
    else:
        form_data = request.form

    form = TenantRegisterForm()

    if form.validate_on_submit():
        user = register_user(form.organization_name.data, **form.to_dict())
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

    return _security.render_template('security/tenant_register.html',
                                     register_user_form=form,
                                     **_ctx('register'))

@bp.route('/register', methods=['GET', 'POST'], subdomain="<subdomain>")
@anonymous_user_required
def register(subdomain):
    """View function which handles a registration request."""
    tenant = Tenant.query.filter_by(subdomain=subdomain).first()
    if tenant is None:
        return redirect(url_for('security.tenant_register'))

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
        user = register_user(**form.to_dict())
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

    return _security.render_template(config_value('REGISTER_USER_TEMPLATE'),
                                     register_user_form=form,
                                     **_ctx('register'))

@bp.route('/p/login', methods=['GET', 'POST'])
def send_login():
    """View function that sends login instructions for passwordless login"""

    form_class = _security.passwordless_login_form

    if request.is_json:
        form = form_class(MultiDict(request.get_json()))
    else:
        form = form_class()

    if form.validate_on_submit():
        send_login_instructions(form.user)
        if not request.is_json:
            do_flash(*get_message('LOGIN_EMAIL_SENT', email=form.user.email))

    if request.is_json:
        return _render_json(form)

    return _security.render_template(config_value('SEND_LOGIN_TEMPLATE'),
                                     send_login_form=form,
                                     **_ctx('send_login'))

@bp.route('/token', methods=['GET', 'POST'])
@anonymous_user_required
def token_login(token):
    """View function that handles passwordless login via a token"""

    expired, invalid, user = login_token_status(token)

    if invalid:
        do_flash(*get_message('INVALID_LOGIN_TOKEN'))
    if expired:
        send_login_instructions(user)
        do_flash(*get_message('LOGIN_EXPIRED', email=user.email,
                              within=_security.login_within))
    if invalid or expired:
        return redirect(url_for('security.login'))

    login_user(user)
    after_this_request(_commit)
    do_flash(*get_message('PASSWORDLESS_LOGIN_SUCCESSFUL'))

    return redirect(get_post_login_redirect())

@bp.route('/confirm/user', methods=['GET', 'POST'])
def send_confirmation():
    """View function which sends confirmation instructions."""

    form_class = _security.send_confirmation_form

    if request.is_json:
        form = form_class(MultiDict(request.get_json()))
    else:
        form = form_class()

    if form.validate_on_submit():
        send_confirmation_instructions(form.user)
        if not request.is_json:
            do_flash(*get_message('CONFIRMATION_REQUEST',
                     email=form.user.email))

    if request.is_json:
        return _render_json(form)

    return _security.render_template(
        config_value('SEND_CONFIRMATION_TEMPLATE'),
        send_confirmation_form=form,
        **_ctx('send_confirmation')
    )

@bp.route('/confirm/email', methods=['GET', 'POST'])
def confirm_email(token):
    """View function which handles a email confirmation request."""

    expired, invalid, user = confirm_email_token_status(token)

    if not user or invalid:
        invalid = True
        do_flash(*get_message('INVALID_CONFIRMATION_TOKEN'))

    already_confirmed = user is not None and user.confirmed_at is not None

    if expired and not already_confirmed:
        send_confirmation_instructions(user)
        do_flash(*get_message('CONFIRMATION_EXPIRED', email=user.email,
                              within=_security.confirm_email_within))
    if invalid or (expired and not already_confirmed):
        return redirect(get_url(_security.confirm_error_view) or
                        url_for('security.send_confirmation'))

    if user != current_user:
        logout_user()
        login_user(user)

    if confirm_user(user):
        after_this_request(_commit)
        msg = 'EMAIL_CONFIRMED'
    else:
        msg = 'ALREADY_CONFIRMED'

    do_flash(*get_message(msg))

    return redirect(get_url(_security.post_confirm_view) or
                    get_url(_security.post_login_view))

@bp.route('/forgot', methods=['GET', 'POST'])
@anonymous_user_required
def forgot_password():
    """View function that handles a forgotten password request."""

    form_class = _security.forgot_password_form

    if request.is_json:
        form = form_class(MultiDict(request.get_json()))
    else:
        form = form_class()

    if form.validate_on_submit():
        send_reset_password_instructions(form.user)
        if not request.is_json:
            do_flash(*get_message('PASSWORD_RESET_REQUEST',
                     email=form.user.email))

    if request.is_json:
        return _render_json(form, include_user=False)

    return _security.render_template(config_value('FORGOT_PASSWORD_TEMPLATE'),
                                     forgot_password_form=form,
                                     **_ctx('forgot_password'))

@bp.route('/reset', methods=['GET', 'POST'])
@anonymous_user_required
def reset_password(token):
    """View function that handles a reset password request."""

    expired, invalid, user = reset_password_token_status(token)

    if invalid:
        do_flash(*get_message('INVALID_RESET_PASSWORD_TOKEN'))
    if expired:
        send_reset_password_instructions(user)
        do_flash(*get_message('PASSWORD_RESET_EXPIRED', email=user.email,
                              within=_security.reset_password_within))
    if invalid or expired:
        return redirect(url_for('security.forgot_password'))

    form = _security.reset_password_form()

    if form.validate_on_submit():
        after_this_request(_commit)
        update_password(user, form.password.data)
        do_flash(*get_message('PASSWORD_RESET'))
        login_user(user)
        return redirect(get_url(_security.post_reset_view) or
                        get_url(_security.post_login_view))

    return _security.render_template(
        config_value('RESET_PASSWORD_TEMPLATE'),
        reset_password_form=form,
        reset_password_token=token,
        **_ctx('reset_password')
    )

@bp.route('/password', methods=['GET', 'POST'])
@login_required
def change_password():
    """View function which handles a change password request."""

    form_class = _security.change_password_form

    if request.is_json:
        form = form_class(MultiDict(request.get_json()))
    else:
        form = form_class()

    if form.validate_on_submit():
        after_this_request(_commit)
        change_user_password(current_user._get_current_object(),
                             form.new_password.data)
        if not request.is_json:
            do_flash(*get_message('PASSWORD_CHANGE'))
            return redirect(get_url(_security.post_change_view) or
                            get_url(_security.post_login_view))

    if request.is_json:
        form.user = current_user
        return _render_json(form)

    return _security.render_template(
        config_value('CHANGE_PASSWORD_TEMPLATE'),
        change_password_form=form,
        **_ctx('change_password')
    )

def register_user(*args, **kwargs):
    confirmation_link, token = None, None
    kwargs['password'] = hash_password(kwargs['password'])
    user = _datastore.create_user(**kwargs)
    _datastore.commit()
    if len(args) > 0:
        tenant = Tenant(
                    name=args[0],
                    subdomain=''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))
        tenant.add_user(user)
        db.session.add(tenant)
        db.session.commit()

    if _security.confirmable:
        confirmation_link, token = generate_confirmation_link(user)
        do_flash(*get_message('CONFIRM_REGISTRATION', email=user.email))

    user_registered.send(current_app._get_current_object(),
                         user=user, confirm_token=token)

    if config_value('SEND_REGISTER_EMAIL'):
        send_mail(config_value('EMAIL_SUBJECT_REGISTER'), user.email,
                  'welcome', user=user, confirmation_link=confirmation_link)

    return user

def register_user2(*args, **kwargs):
    confirmation_link, token = None, None
    print(kwargs)
    kwargs['password'] = hash_password(kwargs['password'])
    user = _datastore.create_user(**kwargs)
    _datastore.commit()
    if len(args) > 0:
        tenant = Tenant(
                    name=args[0],
                    subdomain=''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))
        tenant.add_user(user)
        db.session.add(tenant)
        db.session.commit()

    if _security.confirmable:
        confirmation_link, token = generate_confirmation_link(user)
        do_flash(*get_message('CONFIRM_REGISTRATION', email=user.email))

    user_registered.send(app._get_current_object(),
                         user=user, confirm_token=token)

    if config_value('SEND_REGISTER_EMAIL'):
        send_mail(config_value('EMAIL_SUBJECT_REGISTER'), user.email,
                  'welcome', user=user, confirmation_link=confirmation_link)

    return user
