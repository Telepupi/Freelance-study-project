from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import current_user, login_required
from ..db import get_cursor

bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates/admin')


def check_admin():
    if current_user.role_id != 3:
        flash("Нет доступа", "error")
        return False
    return True

@bp.route('/users')
@login_required
def admin_users():
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        return render_template('admin_users.html', users=users)
    finally:
        cur.close()


@bp.route('/delete_user/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        conn.commit()
        flash("Пользователь удалён", "success")
    finally:
        cur.close()
    return redirect(url_for('admin.admin_users'))


@bp.route('/categories', methods=['GET', 'POST'])
@login_required
def admin_categories():
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            if name:
                cur.execute("INSERT INTO categories(name) VALUES (%s)", (name,))
                conn.commit()
                flash("Категория добавлена", "success")
        cur.execute("SELECT * FROM categories")
        categories = cur.fetchall()
        return render_template('admin_categories.html', categories=categories)
    finally:
        cur.close()


@bp.route('/delete_category/<category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        cur.execute("DELETE FROM categories WHERE category_id=%s", (category_id,))
        conn.commit()
        flash("Категория удалена", "success")
    finally:
        cur.close()
    return redirect(url_for('admin.admin_categories'))


@bp.route('/reviews')
@login_required
def admin_reviews():
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        cur.execute("SELECT * FROM reviews")
        reviews = cur.fetchall()
        return render_template('admin_reviews.html', reviews=reviews)
    finally:
        cur.close()


@bp.route('/delete_review/<review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        cur.execute("DELETE FROM reviews WHERE review_id=%s", (review_id,))
        conn.commit()
        flash("Отзыв удалён", "success")
    finally:
        cur.close()
    return redirect(url_for('admin.admin_reviews'))


@bp.route('/orders')
@login_required
def admin_orders():
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        cur.execute("SELECT * FROM orders")
        orders = cur.fetchall()
        return render_template('admin_orders.html', orders=orders)
    finally:
        cur.close()


@bp.route('/delete_order/<order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        cur.execute("DELETE FROM orders WHERE order_id=%s", (order_id,))
        conn.commit()
        flash("Заказ удалён", "success")
    finally:
        cur.close()
    return redirect(url_for('admin.admin_orders'))


@bp.route('/bids')
@login_required
def admin_bids():
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        cur.execute("SELECT * FROM bids")
        bids = cur.fetchall()
        return render_template('admin_bids.html', bids=bids)
    finally:
        cur.close()


@bp.route('/delete_bid/<bid_id>', methods=['POST'])
@login_required
def delete_bid(bid_id):
    if not check_admin():
        return redirect(url_for('home.homepage'))
    cur, conn = get_cursor()
    try:
        cur.execute("DELETE FROM bids WHERE bid_id=%s", (bid_id,))
        conn.commit()
        flash("Отклик удалён", "success")
    finally:
        cur.close()
    return redirect(url_for('admin.admin_bids'))
