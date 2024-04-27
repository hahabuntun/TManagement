from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
# from config import Config
from flask_migrate import Migrate


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


# Функция создания приложения
def create_app():
    app = Flask(__name__)


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

#     # Загрузка blueprints
#     from src.errors import bp as errors_bp
#     app.register_blueprint(errors_bp)
#
#     from app.auth import bp as auth_bp
#     app.register_blueprint(auth_bp, url_prefix='/auth')
#
#     from app.main import bp as main_bp
#     app.register_blueprint(main_bp)
#
#     from app.api import bp as api_bp
#     app.register_blueprint(api_bp, url_prefix='/api')
#
#     return app
#
#
# from app import models


if __name__ == "__main__":
    app = create_app()
    app.run()
