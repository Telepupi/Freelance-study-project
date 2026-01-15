from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from unicodedata import category

from app.db import get_cursor


bp = Blueprint('orders', __name__, url_prefix='/orders', template_folder='../templates/orders')

@bp.route('/')
@login_required
def list_orders():
    status = request.args.get('status')
    category = request.args.get('category')
    price_from = request.args.get('price_from')
    price_to = request.args.get('price_to')
    cur, conn = get_cursor()
    try:
        com = """SELECT o.order_id, o.title, o.description, o.budget, o.deadline, o.status, c.category_id 
        AS category_id, c.name AS category_name FROM orders o LEFT JOIN categories c ON o.category_id = c.category_id WHERE 1=1 """
        params = []
        if status:
            com += "AND status = %s"
            params.append(status)
        if price_from:
            com += "AND budget >= %s"
            params.append(price_from)
        if price_to:
            com += "AND budget <= %s"
            params.append(price_to)
        if category:
            com += "AND o.category_id = %s"
            params.append(category)
        cur.execute(com, params)
        result = cur.fetchall()
        cur.execute("SELECT * FROM categories")
        categories = cur.fetchall()
        return render_template('orders.html', data=result, category = categories)
    except Exception as e:
        return f'error:{e}'
    finally:
        cur.close()

# TODO: выбор категории выпадающим списком атегория при создании
@bp.route('/create', methods=['POST', 'GET'])
@login_required
def create_order():
        cur, conn = get_cursor()
        try:
            cur.execute("SELECT category_id, name FROM categories ORDER BY name")
            category = cur.fetchall()
            if request.method == 'POST':
                if not all([request.form.get('title'), request.form.get('description'), request.form.get('budget'),
                            request.form.get('deadline'), request.form.get('category_id')]):
                        flash('Заполните все поля', 'error')
                        return redirect(url_for('orders.create_order'))
                if not ('2025-01-01' <= request.form['deadline'] <= '2026-12-31'):
                    flash('Дата должна быть между 2025-01-01 и 2026-12-31', 'error')
                    return render_template('create_order.html', category=category)
                cur.execute(
                'INSERT INTO orders(title, description, budget, deadline, customer_id, category_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING order_id',
                (request.form['title'], request.form['description'], int(request.form['budget']), request.form['deadline'], current_user.user_id, int(request.form['category_id']),)
                )
                order_id = cur.fetchone()['order_id']
                conn.commit()
                flash('Заказ успешно создан', 'success')
                return redirect(url_for('orders.order_card', order_id=order_id))
            return render_template('create_order.html', category=category)
        except Exception as e:
            flash(f'ошибка {e}', 'error')
            return redirect('/')
        finally:
            cur.close()

@bp.route('/edit_order/<order_id>', methods=['POST', 'GET'])
@login_required
def edit_order(order_id):
    cur, conn = get_cursor()
    try:
        cur.execute("SELECT category_id, name FROM categories")
        categories = cur.fetchall()

        cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cur.fetchone()

        if not order:
            flash('Заказ не найден', 'error')
            return redirect(url_for('orders.list_orders'))

        if order['customer_id'] != current_user.user_id:
            flash('Нет доступа для редактирования этого заказа', 'error')
            return redirect(url_for('orders.order_card', order_id=order_id))

        if request.method == 'POST':
            fields = ['title', 'description', 'budget', 'deadline', 'category_id']
            update_fields = []
            values = []

            for f in fields:
                value = request.form.get(f)
                if value:
                    if f in ['budget', 'category_id']:
                        value = int(value)
                    update_fields.append(f'{f} = %s')
                    values.append(value)
            if not update_fields:
                flash('Ничего не изменено', 'error')
                return redirect(url_for('orders.order_card', order_id=order_id))
            values.append(order_id)
            command = f"UPDATE orders SET {', '.join(update_fields)} WHERE order_id = %s"
            cur.execute(command, values)
            conn.commit()
            flash('Заказ успешно обновлён', 'success')
            return redirect(url_for('orders.order_card', order_id=order_id))
        return render_template('edit_order.html', order=order, categories=categories)
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
        return redirect(url_for('orders.list_orders'))
    finally:
        cur.close()

#8 - cust 9 - free
@bp.route('/<order_id>')
@login_required
def order_card(order_id):
    cur, conn = get_cursor()
    try:
        cur.execute('SELECT * FROM orders WHERE order_id = %s', (order_id,))
        order = cur.fetchone()
        cur.execute('SELECT name FROM categories WHERE category_id = %s', (order["category_id"],))
        category = cur.fetchone()
        cur.execute('SELECT * FROM customer_profiles WHERE customer_id = %s', (order["customer_id"],))
        customer = cur.fetchone()
        cur.execute('SELECT username FROM users WHERE user_id = %s', (order['customer_id'],))
        row = cur.fetchone()
        customer = dict(customer)
        customer['username'] = row[0] if row else None
        #выбранный исполнитель
        cur.execute('SELECT first_name, last_name FROM freelancer_profiles WHERE freelancer_id = %s', (order["freelancer_id"],))
        freelancer = cur.fetchone()
        cur.execute("""
            SELECT b.*, f.first_name, f.last_name, u.username
            FROM bids b
            JOIN freelancer_profiles f ON b.freelancer_id = f.freelancer_id
            JOIN users u ON b.freelancer_id = u.user_id
            WHERE b.order_id = %s
        """, (order_id,))
        bids = cur.fetchall()
        print(bids)
        return render_template('order_card.html',
                               order = order, category = category, customer = customer,
                               freelancer = freelancer, bids=bids)

    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
        return redirect('/')
    finally:
        cur.close()

#TODO: Исправить везде EXception Как тут

@bp.route('/complete_order/<order_id>', methods = ['POST'])
@login_required
def complete_order(order_id):
    cur, conn = get_cursor()
    try:
        cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cur.fetchone()
        if order['status'] != 'in_progress':
            flash("Заказ нельзя подтвердить", "error")
            return redirect(request.referrer)
        if current_user.user_id == order['freelancer_id']:
            cur.execute("UPDATE orders SET status = 'under_checking' WHERE order_id = %s", (order_id,))
            conn.commit()
        else:
            flash('вы не можете подтвердить, так как вы не являетесь исполнителем', 'error')
            return redirect(request.referrer)
        flash("Вы отметили заказ как выполненный. Ожидается подтверждение заказчика.", "success")
        return redirect(request.referrer)
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
        return redirect(request.referrer)
    finally:
        cur.close()

@bp.route('/close_order/<order_id>', methods = ['POST'])
@login_required
def close_order(order_id):
    cur, conn = get_cursor()
    try:
        cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cur.fetchone()
        if order['status'] != 'under_checking':
            flash("Заказ нельзя завершить", "error")
            return redirect(request.referrer)
        if current_user.user_id == order['customer_id']:
            cur.execute("UPDATE orders SET status = 'completed' WHERE order_id = %s", (order_id,))
            conn.commit()
        else:
            flash('вы не можете завершить заказ, так как не являетесь заказчиком', 'error')
            return redirect(request.referrer)
        flash("Вы успешно подтвердили выполнение заказа", "success")
        return redirect(request.referrer)
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
        return redirect(request.referrer)
    finally:
        cur.close()

@bp.route('/reject_order/<order_id>', methods = ['POST'])
@login_required
def reject_order(order_id):
    cur, conn = get_cursor()
    try:
        cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cur.fetchone()
        if order['status'] != 'under_checking':
            flash("Заказ нельзя отклонить", "error")
            return redirect(request.referrer)
        if current_user.user_id == order['customer_id']:
            cur.execute("UPDATE orders SET status = 'in_progress' WHERE order_id = %s", (order_id,))
            conn.commit()
        else:
            flash('вы не можете завершить заказ, так как не являетесь заказчиком', 'error')
            return redirect(request.referrer)
        flash("Вы отклонили завершение заказа", "success")
        return redirect(request.referrer)
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
        return redirect(request.referrer)
    finally:
        cur.close()