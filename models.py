from flask_mysqldb import MySQL

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


def init_app(app):
    mysql.init_app(app)
