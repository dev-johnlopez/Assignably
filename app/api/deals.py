from flask import jsonify, request, url_for, g, current_app, render_template
from app import db
from app.deals.models import Deal
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.email import send_email
from flask_cors import cross_origin


@bp.route('/deals/<int:id>', methods=['GET'])
@token_auth.login_required
def get_deal(id):
    pass


@bp.route('/deals', methods=['GET'])
@token_auth.login_required
def get_deals():
    return ''


@bp.route('/deals', methods=['POST'])
@token_auth.login_required
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def create_deal():
    data = request.get_json() or {}
    if 'address' not in data \
        or 'sq_feet' not in data \
        or 'bedrooms_str' not in data \
        or 'bathrooms_str' not in data \
        or 'after_repair_value' not in data \
            or 'rehab_estimate' not in data or 'purchase_price' not in data:
        return bad_request('Missing Required Fields.')
    deal = Deal()
    deal.from_dict(data)
    db.session.add(deal)
    db.session.commit()
    recipient = g.current_user.email
    if g.current_user.getSettings().partnership_email_recipient is not None:
        recipient = g.current_user.getSettings().partnership_email_recipient
    send_email('New Deal Notification!',
               sender='support@assignably.com', recipients=[recipient],
               text_body=render_template('emails/new_deal.txt',
                                         user=g.current_user,
                                         deal=deal),
               html_body=render_template('emails/new_deal.html',
                                         user=g.current_user,
                                         deal=deal),
               attachments=[],
               sync=True)

    response = jsonify(deal.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_deal', id=deal.id)
    return response


@bp.route('/deals/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_deal(id):
    pass
