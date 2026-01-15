from flask import Blueprint, render_template

bp = Blueprint('home', __name__, template_folder='../templates/home')
@bp.route('/')
def homepage():
    return render_template("home.html")
