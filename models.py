from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


mysql = MySQL()

def save_token(user_id, token):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tokens(user_id, token) VALUES (%s, %s)", (user_id, token))
    mysql.connection.commit()
    cur.close()

def delete_token(token):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tokens WHERE token = %s", (token,))
    mysql.connection.commit()
    cur.close()

def token_exists(token):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tokens WHERE token = %s", (token,))
    token_data = cur.fetchone()
    cur.close()
    return token_data is not None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    roles = db.relationship('Role', backref='user', lazy=True)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def init_app(app):
    mysql.init_app(app)
