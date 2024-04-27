from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


# Функция создания приложения
def create_app(config_class=Config):
    app = Flask(__name__)
    # Загрузка настроек из Config
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Загрузка blueprints
    from project.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from project.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from project.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app


from project import models
