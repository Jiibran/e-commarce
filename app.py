from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, decode_token
from config import Config
from models import init_app, mysql, token_exists, save_token, delete_token
from routes import auth_bp, product_bp, cart_bp, order_bp, payment_bp, shipping_bp
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": "http://174.138.27.151:8081"}}) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'  # Or other database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
jwt = JWTManager(app)
init_app(app)

def create_tables():
    with app.app_context():
        db.create_all(bind='roles') 
        db.create_all()

@app.cli.command("create-db")
def create_db_command():
    """Creates the database tables."""
    create_tables()
    print("Database tables created.")

@app.route('/')
def home():
    return 'E-commerce API is running'
    

# @jwt.token_in_blocklist_loader
# def check_if_token_in_blocklist(jwt_header, jwt_payload):
#    jti = jwt_payload['jti']
#    return not token_exists(jti)
blocklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in blocklist

# @jwt.revoked_token_loader
# def revoked_token_callback(jwt_header, jwt_payload):
#     return jsonify({"msg": "Token has been revoked"}), 401

@app.errorhandler(401)
def custom_401(error):
    return jsonify({'message': 'Invalid or expired token'}), 401

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(product_bp, url_prefix='/api')
app.register_blueprint(cart_bp, url_prefix='/api')
app.register_blueprint(order_bp, url_prefix='/api')
app.register_blueprint(payment_bp, url_prefix='/api')
app.register_blueprint(shipping_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)