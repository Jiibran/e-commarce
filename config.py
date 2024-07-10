import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    MYSQL_HOST = 'host.docker.internal'
    MYSQL_USER = 'user'
    MYSQL_PASSWORD = 'password'
    MYSQL_DB = 'dbname'


