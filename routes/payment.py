from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import payment_bp
from models import mysql, save_token, delete_token, token_exists

@payment_bp.route('/payments', methods=['POST'])
@jwt_required()
def process_payment():
    user_id = get_jwt_identity()
    data = request.get_json()
    order_id = data['order_id']
    payment_method = data['payment_method']
    cur = mysql.connection.cursor()
    cur.execute("SELECT total_price FROM orders WHERE id = %s AND user_id = %s", (order_id, user_id))
    order = cur.fetchone()
    if order:
        cur.execute("INSERT INTO payments(order_id, user_id, amount, method, status) VALUES (%s, %s, %s, %s, 'completed')", (order_id, user_id, order[0], payment_method))
        payment_id = cur.lastrowid
        cur.execute("UPDATE orders SET status = 'paid' WHERE id = %s", (order_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Payment processed successfully', 'payment_id': payment_id})
    else:
        cur.close()
        return jsonify({'message': 'Order not found'}), 404

@payment_bp.route('/payments/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment_status(payment_id):
    user_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM payments WHERE id = %s AND user_id = %s", (payment_id, user_id))
    payment = cur.fetchone()
    cur.close()
    if payment:
        return jsonify({'payment_id': payment[0], 'order_id': payment[1], 'amount': payment[3], 'method': payment[4], 'status': payment[5], 'paid_at': payment[6]})
    else:
        return jsonify({'message': 'Payment not found'}), 404
