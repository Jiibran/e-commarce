from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import product_bp
from models import mysql, save_token, delete_token, token_exists

@product_bp.route('/products', methods=['GET'])
def get_products():
    category_id = request.args.get('category_id', None)
    cur = mysql.connection.cursor()

    if category_id:
        # Query to fetch products by category
        cur.execute("""
            SELECT p.* FROM products p
            JOIN product_categories pc ON p.id = pc.product_id
            WHERE pc.category_id = %s
        """, (category_id,))
    else:
        # Query to fetch all products if no category_id is provided
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
    categories = data.get('categories', [])  # Expect categories to be a list of category IDs

    cur = mysql.connection.cursor()
    # Insert the product
    cur.execute("INSERT INTO products(name, description, price, stock, image_url) VALUES (%s, %s, %s, %s, %s)", (name, description, price, stock, image_url))
    product_id = cur.lastrowid  # Get the ID of the newly inserted product

    # Insert product-category relationships
    for category_id in categories:
        cur.execute("INSERT INTO product_categories(product_id, category_id) VALUES (%s, %s)", (product_id, category_id))

    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'Product added successfully with categories'})

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()  # Optional: Require authentication to update a product
def update_product(product_id):
    # Retrieve new product details from the request body
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock')
    image_url = data.get('image_url')

    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the update query
    cur.execute("""
        UPDATE products
        SET name = %s, description = %s, price = %s, stock = %s, image_url = %s
        WHERE id = %s
    """, (name, description, price, stock, image_url, product_id))

    # Commit the changes to the database
    mysql.connection.commit()
    cur.close()

    # Check if any row was affected
    if cur.rowcount == 0:
        return jsonify({'message': 'Product not found or no update made'}), 404

    return jsonify({'message': 'Product updated successfully'})

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()  # Optional: Require authentication to delete a product
def delete_product(product_id):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the DELETE query
    cur.execute("DELETE FROM products WHERE id = %s", (product_id,))

    # Commit the changes to the database
    mysql.connection.commit()

    # Check if any row was affected
    if cur.rowcount == 0:
        cur.close()
        return jsonify({'message': 'Product not found'}), 404

    cur.close()
    return jsonify({'message': 'Product deleted successfully'})
