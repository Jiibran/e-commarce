from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from . import auth_bp
from models import mysql, save_token, delete_token, token_exists, db, User, Role, Order

app = Flask(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = generate_password_hash(data['password'])
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users(username, email, password) VALUES (%s, %s, %s)", (username, email, password))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'User registered successfully'})

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    if user and check_password_hash(user[3], password):
        token = create_access_token(identity=user[0])
        save_token(user[0], token)
        return jsonify({'token': token, 'user_id': user[0]})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    token = request.headers['Authorization'].split(' ')[1]
    delete_token(token)
    return jsonify({'message': 'User logged out successfully'})

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return jsonify({'user_id': user[0], 'username': user[1], 'email': user[2]})

@app.route('/all-orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Check if the user has a seller role
    is_seller = any(role.role_name == 'seller' for role in user.roles)
    
    if is_seller:
        # Fetch all orders for sellers
        orders = Order.query.all()
    else:
        # Fetch only orders for the current user
        orders = Order.query.filter_by(user_id=current_user_id).all()
    
    orders_data = [{'id': order.id, 'details': order.details} for order in orders]
    return jsonify(orders_data)