from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import shipping_bp
from models import mysql

@shipping_bp.route('/orders/<int:order_id>/shipping', methods=['PUT'])
@jwt_required()
def update_shipping_status(order_id):
    data = request.get_json()
    status = data['status']
    tracking_number = data.get('tracking_number', None)
    cur = mysql.connection.cursor()
    cur.execute("UPDATE orders SET status = %s, tracking_number = %s WHERE id = %s", (status, tracking_number, order_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Shipping status updated successfully'})
