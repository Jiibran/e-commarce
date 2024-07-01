from flask import Blueprint

auth_bp = Blueprint('auth_bp', __name__)
product_bp = Blueprint('product_bp', __name__)
cart_bp = Blueprint('cart_bp', __name__)
order_bp = Blueprint('order_bp', __name__)
payment_bp = Blueprint('payment_bp', __name__)
shipping_bp = Blueprint('shipping_bp', __name__)

from .auth import *
from .product import *
from .cart import *
from .order import *
from .payment import *
from .shipping import *


from models import mysql, save_token, delete_token, token_exists
