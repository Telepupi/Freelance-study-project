import os

from dotenv import load_dotenv
from flask import Flask

from app.flogin import login_manager
from app.user import User
from app.routes.admin import bp as admin_bp
from app.routes.errors import bp as errors_bp
from app.routes.home import bp as home_bp
from app.routes.orders import bp as orders_bp
from app.routes.auth import bp as auth_bp
from app.routes.profile import bp as profile_bp
from app.routes.bids import bp as bids_bp
from app.routes.reviews import bp as reviews_bp

load_dotenv('config.env', encoding='utf-8')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    login_manager.init_app(app)
    blueprints = [admin_bp, orders_bp, home_bp, errors_bp, auth_bp, profile_bp, bids_bp, reviews_bp]
    for elem in blueprints:
        app.register_blueprint(elem)
    return app

