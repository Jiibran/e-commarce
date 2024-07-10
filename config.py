import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    MYSQL_HOST = 'localhost'  # Updated to use the container name
    MYSQL_USER = 'user'
    MYSQL_PASSWORD = 'password'
    MYSQL_DB = 'dbname'