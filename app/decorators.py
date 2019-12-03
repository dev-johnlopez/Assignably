from functools import wraps
from flask import g, request, redirect, url_for, render_template, request, \
                    flash, current_app
from flask_security import current_user

def login_required(func):
    '''
    If you decorate a view with this, it will ensure that the current user is
    logged in and authenticated before calling the actual view. (If they are
    not, it calls the :attr:`LoginManager.unauthorized` callback.) For
    example::

        @app.route('/post')
        @login_required
        def post():
            pass

    If there are only certain times you need to require that your user is
    logged in, you can do so with::

        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

    ...which is essentially the code that this function adds to your views.

    It can be convenient to globally turn off authentication when unit testing.
    To enable this, if the application configuration variable `LOGIN_DISABLED`
    is set to `True`, this decorator will be ignored.

    .. Note ::

        Per `W3 guidelines for CORS preflight requests
        <http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0>`_,
        HTTP ``OPTIONS`` requests are exempt from login checks.

    :param func: The view function to decorate.
    :type func: function
    '''
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if False:#request.method in EXEMPT_METHODS:
            print("Exempt")
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            print("disabled")
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            print("not authenticated")
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view

def tenant_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated and current_user.tenant is None:
            print("no tenant")
            flash('Tenant is required', 'danger')
            return redirect(url_for('security.login'))
        return func(*args, **kwargs)
    return decorated_view
