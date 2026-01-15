from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = "home.homepage"
login_manager.login_message ="Пожалуйста, войдите, чтобы увидеть содержимое"