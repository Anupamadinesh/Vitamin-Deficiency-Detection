from flask_login import UserMixin
from . import mysql, login_manager


class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def get_by_email(email):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users1 WHERE email = %s", (email,))
        data = cur.fetchone()
        cur.close()
        if data:
            return User(data['id'], data['username'], data['email'], data['password'])
        return None

    @staticmethod
    def get_by_id(id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users1 WHERE id = %s", (id,))
        data = cur.fetchone()
        cur.close()
        if data:
            return User(data['id'], data['username'], data['email'], data['password'])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)
  


