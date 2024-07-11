from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import order_bp
from models import mysql, save_token, delete_token, token_exists
import sqlite3

@order_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("SELECT p.id, p.price, c.quantity FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id = %s", (user_id,))
    cart_items = cur.fetchall()
    total_price = sum(item[1] * item[2] for item in cart_items)
    cur.execute("INSERT INTO orders(user_id, total_price, status) VALUES (%s, %s, 'pending')", (user_id, total_price))
    order_id = cur.lastrowid
    for item in cart_items:
        cur.execute("INSERT INTO order_items(order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)", (order_id, item[0], item[2], item[1]))
    cur.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Order created successfully', 'order_id': order_id})

@order_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    user_email = get_jwt_identity()
    print(user_email)
    # Connect to the SQLite database to check user roles
    sqlite_conn = sqlite3.connect('yourdatabase.db')  # Update the path to your SQLite DB
    sqlite_cur = sqlite_conn.cursor()
    sqlite_cur.execute("SELECT role FROM users WHERE email = ?", (user_email,))
    is_admin = sqlite_cur.fetchone()
    sqlite_cur.close()
    sqlite_conn.close()
    
    # Connect to MySQL to fetch orders
    cur = mysql.connection.cursor()
    if is_admin and is_admin[0] == 'admin':
        # If the user is an admin, fetch all orders
        cur.execute("SELECT * FROM orders")
    else:
        # If the user is not an admin, fetch orders only for that user
        cur.execute("SELECT * FROM orders WHERE user_id = %s", (user_email,))
    
    orders = cur.fetchall()
    cur.close()
    
    # Format and return the orders
    return jsonify([{'order_id': o[0], 'user_email': o[1], 'total_price': o[2], 'status': o[3], 'created_at': o[4]} for o in orders])

@order_bp.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE id = %s AND user_id = %s", (order_id, user_id))
    order = cur.fetchone()
    if order:
        cur.execute("SELECT p.id, p.name, oi.quantity, oi.price FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = %s", (order_id,))
        items = cur.fetchall()
        cur.close()
        return jsonify({'order_id': order[0], 'total_price': order[2], 'status': order[3], 'created_at': order[4], 'products': [{'product_id': i[0], 'name': i[1], 'quantity': i[2], 'price': i[3]} for i in items]})
    else:
        cur.close()
        return jsonify({'message': 'Order not found'}), 404
