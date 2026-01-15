from flask import Blueprint, request, flash, redirect, render_template, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import User
from app.db import get_cursor

bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='../templates/auth')

@bp.route('/registration', methods=["GET","POST"])
def registration():
    if request.method == "POST":
        cur, conn = get_cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        role_id = int(request.form.get('role'))
        try:
            if username and password and role_id:
                cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                existing_user = cur.fetchone()
                if existing_user:
                    flash(f"Логин занят", 'error')
                    return redirect(request.referrer)
                password_hash = generate_password_hash(password)
                cur.execute("INSERT INTO users(username, password_hash, role_id) VALUES (%s, %s, %s) RETURNING user_id", (
                    username, password_hash, role_id))
                user_id = cur.fetchone()[0]
                if role_id == 1:
                    cur.execute("INSERT INTO freelancer_profiles(freelancer_id, first_name, last_name) VALUES (%s, %s, %s)", (user_id, '', ''))
                if role_id == 2:
                    cur.execute("INSERT INTO customer_profiles(customer_id) VALUES (%s)", (user_id,))
                conn.commit()
                user = User(user_id = user_id, username=username, password_hash = password_hash, role_id = role_id)
                login_user(user)
                flash(f"Пользователь {username} успешно добавлен", 'success')
                return redirect(f'/profile/{username}')
            else:
                flash('Заполните ВСЕ поля', 'error')
        except Exception as e:
            flash(f'Ошибка: {e}', 'error')
            return redirect('/')
        finally:
            conn.close()
    return render_template('registration.html')

@bp.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        cur, conn = get_cursor()
        try:
            username = request.form['username']
            password = request.form['password']
            if not username or not password:
                flash('Запоните все поля', 'error')
            cur.execute('SELECT user_id, username, password_hash, role_id FROM USERS WHERE username = %s', (username,))
            row = cur.fetchone()
            if row:
                user = User(row['user_id'], row['username'], row['password_hash'], row['role_id'])
                if check_password_hash(user.password_hash, password):
                    login_user(user)
                    if row['role_id'] == 3:
                        return redirect("/admin/users")
                    return redirect(f'/profile/{username}')
                else:
                    flash('неверный пароль', 'error')
            else:
                flash('такого пользователя не существует', 'error')
        except Exception as e:
            flash(f'Ошибка: {e}', 'error')
            return redirect('/')
        finally:
            conn.close()
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.homepage'))