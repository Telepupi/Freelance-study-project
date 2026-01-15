from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app.db import get_cursor

bp = Blueprint('bids',__name__, url_prefix='/bids', template_folder='../templates/bids')

@bp.route('/create_bid/<order_id>', methods = ['GET', 'POST'])
@login_required
def create_bid(order_id):
    if request.method == "POST":
        cur, conn = get_cursor()
        cur.execute("SELECT 1 FROM bids WHERE order_id = %s and freelancer_id = %s", (order_id, current_user.user_id,))
        res = cur.fetchone()
        if res is not None:
            flash('вы не можете создать больше одного отклика на заказ', 'error')
            cur.close()
            return redirect(f'/orders/{order_id}')
        else:
            try:
                cur.execute('INSERT INTO bids(order_id, bid_text, price, deadline, freelancer_id) VALUES (%s, %s, %s, %s, %s)',
                            (order_id, request.form['bid_text'], int(request.form['price']), request.form['deadline'], current_user.user_id, ))
                conn.commit()
            except Exception as e:
                flash(f'ошибка {e}', 'error')
                return redirect('/')
            finally:
                cur.close()
                flash('вы успешно оставили отклик', 'success')
                return redirect(url_for('orders.order_card', order_id = order_id))
    return render_template('create_bid.html')

@bp.route('/accept_bid/<bid_id>', methods = ['POST'])
@login_required
def accept_bid(bid_id):
    cur, conn = get_cursor()
    try:
        cur.execute('SELECT freelancer_id, order_id FROM bids WHERE bid_id = (%s)', (bid_id,))
        bid = cur.fetchone()
        if not bid:
            flash('отклик не найден', 'error')
            return redirect(url_for('orders.list_orders'))
        cur.execute('UPDATE orders SET freelancer_id = %s, status = %s WHERE order_id = %s',
                    (bid['freelancer_id'], 'in_progress', bid['order_id']))
        cur.execute("UPDATE bids SET status = 'accepted' WHERE bid_id = %s", (bid_id,))
        cur.execute("UPDATE bids SET status = 'rejected' WHERE bid_id != %s and order_id = %s", (bid_id, bid['order_id']), )
        conn.commit()
        flash('Отклик принят!', 'success')
        return redirect(url_for('orders.order_card', order_id=bid['order_id']))
    except Exception as e:
         flash(f'ошибка {e}', 'error')
         return redirect(url_for('orders.list_orders'))
    finally:
        conn.close()
