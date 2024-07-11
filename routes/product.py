from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import product_bp
from models import mysql, save_token, delete_token, token_exists
from decimal import Decimal

@product_bp.route('/products', methods=['GET'])
def get_products():
    category_id = request.args.get('category_id', None)
    search_field = request.args.get('searchField', None)
    cur = mysql.connection.cursor()

    if category_id:
        cur.execute("""
            SELECT p.* FROM products p
            JOIN product_categories pc ON p.id = pc.product_id
            WHERE pc.category_id = %s
        """, (category_id,))
    elif search_field:
        search_query = f"%{search_field}%"
        cur.execute("""
            SELECT * FROM products
            WHERE name LIKE %s
        """, (search_query,))
    else:
        cur.execute("SELECT * FROM products")

    products = cur.fetchall()
    cur.close()

    # Convert Decimal to float for JSON serialization
    products_list = [
        {
            'product_id': p[0], 
            'name': p[1], 
            'description': p[2], 
            'price': float(p[3]) if isinstance(p[3], Decimal) else p[3], 
            'stock': p[4],
            # Ensure all necessary fields are included here
        } for p in products
    ]

    return jsonify(products_list)

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    cur.close()
    if product:
        # Convert Decimal to float for JSON serialization
        product_dict = {
            'product_id': product[0], 
            'name': product[1], 
            'description': product[2], 
            'price': float(product[3]) if isinstance(product[3], Decimal) else product[3], 
            'stock': product[4], 
            'image_url': product[5]
        }
        return jsonify(product_dict)
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

@product_bp.route('/categories', methods=['GET'])
def get_all_categories():
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the SELECT query
    cur.execute("SELECT * FROM categories")

    # Fetch all results
    categories = cur.fetchall()

    # Close the cursor
    cur.close()

    # Check if categories were found
    if categories:
        return jsonify({'categories': categories})
    else:
        return jsonify({'message': 'No categories found'}), 404
    
@product_bp.route('/products/<int:product_id>/categories', methods=['GET'])
def get_product_with_categories(product_id):
    # Connect to the database
    cur = mysql.connection.cursor()

    # Execute the SELECT query with JOIN to fetch product and its category
    cur.execute("""
        SELECT p.id, p.name, p.description, p.price, c.id AS category_id, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s
    """, (product_id,))

    # Fetch the result
    product = cur.fetchone()

    # Close the cursor
    cur.close()

    # Check if the product was found
    if product:
        return jsonify({'product': product})
    else:
        return jsonify({'message': 'Product not found'}), 404

@product_bp.route('/product_variants', methods=['GET'])
def get_product_variants():
    product_id = request.args.get('product_id', None)
    if not product_id:
        return {"error": "Product ID is required"}, 400

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT variant_id, product_id, variant_name, price, stock
        FROM product_variants
        WHERE product_id = %s
    """, (product_id,))

    variants = cur.fetchall()
    cur.close()

    # Convert Decimal to float for JSON serialization and prepare the response
    variants_list = [
        {
            'variant_id': v[0],
            'product_id': v[1],
            'variant_name': v[2],
            'price': float(v[3]) if isinstance(v[3], Decimal) else v[3],
            'stock': v[4]
        } for v in variants
    ]

    return {"variants": variants_list}