import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    MYSQL_HOST = '174.138.27.151'  # Updated to use the container name
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'rootpassword'
    MYSQL_DB = 'dbname'