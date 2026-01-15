from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_required, current_user

from app.db import get_cursor

bp = Blueprint('reviews', __name__, url_prefix='/', template_folder = '../templates/review')
@bp.route('/create_review/<order_id>', methods = ["GET", "POST"])
@login_required
def create_review(order_id):
    if request.method == 'POST':
        cur, conn = get_cursor()
        try:
            cur.execute('SELECT freelancer_id, customer_id, status FROM orders WHERE order_id = %s', (order_id,))
            order = cur.fetchone()
            if order['status'] != 'completed':
                flash('Нельзя оставить отзыв до завершения заказа', 'error')
                return redirect(url_for('orders.order_card', order_id=order_id))
            if order is None:
                flash('Ошибка, такой заказ не найден')
                return redirect(url_for('orders.order_card', order_id = order_id))
            if order['freelancer_id'] == current_user.user_id:
                target_id = order['customer_id']
            elif order['customer_id'] == current_user.user_id:
                target_id = order['freelancer_id']
            else:
                flash("у вас нет прав оставлять отзыв на этот заказ", 'error')
                return redirect(url_for('orders.order_card', order_id = order_id))
            cur.execute(
                "SELECT * FROM reviews WHERE author_id=%s AND order_id=%s",
                (current_user.user_id, order_id)
            )
            existing = cur.fetchone()
            if existing:
                flash("Вы уже оставили отзыв на этот заказ", "error")
                return redirect(url_for('orders.order_card', order_id=order_id))
            rating = int(request.form.get('rating'))
            if not(1 <= rating <= 10):
                flash('Рейтинг не может быть больше 10 или меньше 1', 'error')
                return redirect(request.referrer)
            cur.execute('INSERT INTO reviews(author_id, target_id, review_text, rating, order_id) VALUES (%s, %s, %s, %s, %s)',
                        (current_user.user_id, target_id, request.form.get('review_text'), rating, order_id))
            conn.commit()
        except Exception as e:
            flash(f'Ошибка {e}', 'error')
            return redirect(url_for('orders.order_card', order_id = order_id))
        finally:
            cur.close()
    return render_template('review.html')

@bp.route('/list_reviews/<user_id>', methods = ["GET", "POST"])
@login_required
def list_reviews(user_id):
    cur, conn = get_cursor()
    try:
        cur.execute("SELECT * FROM reviews WHERE target_id = %s", (user_id,))
        reviews = cur.fetchall()
        if reviews:
            rating_avg = sum([r['rating'] for r in reviews]) / len(reviews)
        else:
            flash('У этого пользователя нет отзывов', 'error')
            rating_avg = 0
        return render_template('list_reviews.html', reviews = reviews, rating_avg = rating_avg)
    except Exception as e:
        flash(f'Ошибка: {e}', 'error')
        return redirect('/')
    finally:
        cur.close()