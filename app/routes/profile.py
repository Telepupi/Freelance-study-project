from flask import Blueprint, flash, render_template, redirect, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from app.db import get_cursor

bp = Blueprint('profile', __name__, url_prefix='/profile', template_folder = '../templates/profile')

@bp.route('/<username>')
@login_required
def profile(username):
    cur, conn = get_cursor()
    try:
        cur.execute('SELECT user_id, role_id FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        if not user:
            flash("Профиль не найден", "danger")
            return redirect('/')

        if user['role_id'] == 1:
            table_name = 'freelancer_profiles'
            id_field = 'freelancer_id'
            orders_table = 'bids'
            orders_field = 'freelancer_id'
        else:
            table_name = 'customer_profiles'
            id_field = 'customer_id'
            orders_table = 'orders'
            orders_field = 'customer_id'

        cur.execute(f"SELECT * FROM {table_name} WHERE {id_field} = %s", (user['user_id'],))
        profile_data = cur.fetchone()
        if not profile_data:
            flash("Профиль не найден", "danger")
            return redirect('/')

        cur.execute(f"SELECT * FROM {orders_table} WHERE {orders_field} = %s", (user['user_id'],))
        orders_bids = cur.fetchall()

        cur.execute("SELECT 1 FROM reviews WHERE target_id = %s", (user['user_id'],))
        reviews_exist = bool(cur.fetchone())

        return render_template('profile.html', profile=profile_data, orders=orders_bids,
                               reviews=reviews_exist, user = user)

    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
        return redirect(request.referrer)
    finally:
        cur.close()

#TODO: возможно : + добавить поля
@bp.route('/<username>/edit', methods = ['POST', 'GET'])
@login_required
def profile_edit(username):
    if username != current_user.username:
        flash('ошибка доступа','error')
        return redirect('/')
    if request.method == 'POST':
        cur, conn = get_cursor()
        try:
            users_fields = ['username', 'password_hash']
            fields = ['first_name', 'last_name', 'about',
                      'contact_method', 'company_name']
            update_fields = []
            update_fields_users = []
            values = []
            users_values = []
            for f in fields:
                value = request.form.get(f)
                if value and value != "":
                    update_fields.append(f'{f} = %s')
                    values.append(value)
            for e in users_fields:
                value = request.form.get(e)
                if value:
                    if e == 'password':
                        update_fields_users.append('password_hash = %s')
                        users_values.append(generate_password_hash(value))
                    elif e == 'username':
                        update_fields_users.append('username = %s')
                        users_values.append(value)
            print(update_fields_users)
            if len(update_fields) == 0 and len(update_fields_users) == 0:
                flash('Ничего не изменено', 'error')
                return redirect(f'/profile/{username}')
            else:
                if update_fields_users:
                    cur.execute(f"UPDATE users SET {', '.join(update_fields_users)} WHERE user_id = %s",
                                users_values + [current_user.user_id])
                if update_fields:
                    values.append(current_user.user_id)
                    if current_user.role_id == 1:
                        command = f"UPDATE freelancer_profiles SET {', '.join(update_fields)} WHERE freelancer_id = %s"
                    elif current_user.role_id == 2:
                        command = f"UPDATE customer_profiles SET {', '.join(update_fields)} WHERE customer_id = %s"
                    cur.execute(command, values)
                conn.commit()
                flash('Профиль успешно изменен!', 'success')
                return redirect(f'/profile/{username}')
        except Exception as e:
            flash(f'Ошибка: {e}', 'error')
            return redirect(request.referrer)
        finally:
            cur.close()
    return render_template('profile_edit.html')
# values - %s in update_fields