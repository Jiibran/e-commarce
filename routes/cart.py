from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import cart_bp
from models import mysql, save_token, delete_token, token_exists

@cart_bp.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data['product_id']
    quantity = data['quantity']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO cart(user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, quantity))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Product added to cart'})

@cart_bp.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("SELECT p.id, p.name, p.price, c.quantity FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id = %s", (user_id,))
    cart_items = cur.fetchall()
    cur.close()
    return jsonify([{'product_id': item[0], 'name': item[1], 'price': item[2], 'quantity': item[3]} for item in cart_items])

@cart_bp.route('/cart', methods=['PUT'])
@jwt_required()
def update_cart():
    user_id = get_jwt_identity()
    data = request.get_json()
    product_id = data['product_id']
    quantity = data['quantity']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE cart SET quantity = %s WHERE user_id = %s AND product_id = %s", (quantity, user_id, product_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Cart updated successfully'})

@cart_bp.route('/cart/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_from_cart(product_id):
    user_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Product removed from cart'})
