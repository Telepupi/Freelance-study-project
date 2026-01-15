from flask_login import UserMixin
from app.flogin import login_manager
from app.db import get_cursor


class User(UserMixin):
    def __init__(self, user_id, username, password_hash, role_id):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role_id = role_id

    def get_id(self):
        return self.user_id


@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)

    cur, conn = get_cursor()
    cur.execute(
        "SELECT user_id, username, password_hash, role_id FROM users WHERE user_id = %s",
        (user_id,)
    )
    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return User(*row)
