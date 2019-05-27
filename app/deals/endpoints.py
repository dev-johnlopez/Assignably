from flask import Blueprint

bp = Blueprint('deals_api', __name__)

@bp.route('/deals/<int:id>', methods=['GET'])
def get_deal(id):
    pass

@bp.route('/deals', methods=['GET'])
def get_deals():
    pass

@bp.route('/deals', methods=['POST'])
def create_deal():
    pass

@bp.route('/deals/<int:id>', methods=['PUT'])
def update_deal(id):
    pass
