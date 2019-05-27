from flask import jsonify, request, url_for, g, current_app, render_template
from app import db
from app.deals.models import Deal
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.email import send_email

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
def create_deal():
    data = request.get_json() or {}
    if 'address' not in data \
        or 'sq_feet' not in data \
        or 'bedrooms' not in data \
        or 'bathrooms' not in data \
        or 'after_repair_value' not in data \
        or 'rehab_estimate' not in data \
        or 'purchase_price' not in data:
        return bad_request('must include username, email and password fields')
    deal = Deal()
    deal.from_dict(data)
    db.session.add(deal)
    db.session.commit()
    send_email('New Deal Notification!',
                sender=current_app.config['ADMINS'][0], recipients=[g.current_user.email],
                text_body=render_template('emails/new_deal.txt', user=g.current_user, deal=deal),
                html_body=render_template('emails/new_deal.html', user=g.current_user, deal=deal),
                attachments=[],
                sync=True)
    #send_deal_notification_email(g.current_user, deal)
    response = jsonify(deal.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_deal', id=deal.id)
    return response

@bp.route('/deals/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_deal(id):
    pass
