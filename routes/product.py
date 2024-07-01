from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import product_bp
from models import mysql, save_token, delete_token, token_exists

@product_bp.route('/products', methods=['GET'])
def get_products():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    cur.close()
    return jsonify([{'product_id': p[0], 'name': p[1], 'description': p[2], 'price': p[3], 'stock': p[4], 'image_url': p[5]} for p in products])

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()
    if product:
        return jsonify({'product_id': product[0], 'name': product[1], 'description': product[2], 'price': product[3], 'stock': product[4], 'image_url': product[5]})
    else:
        return jsonify({'message': 'Product not found'}), 404

@product_bp.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.get_json()
    name = data['name']
    description = data['description']
    price = data['price']
    stock = data['stock']
    image_url = data['image_url']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO products(name, description, price, stock, image_url) VALUES (%s, %s, %s, %s, %s)", (name, description, price, stock, image_url))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Product added successfully'})

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    data = request.get_json()
    name = data['name']
    description = data['description']
    price = data['price']
    stock = data['stock']
    image_url = data['image_url']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE products SET name = %s, description = %s, price = %s, stock = %s, image_url = %s WHERE id = %s", (name, description, price, stock, image_url, product_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Product updated successfully'})

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Product deleted successfully'})
