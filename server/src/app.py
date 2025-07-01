from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('src.config.Config')
    # Инициализация расширений
    db.init_app(app)
    jwt.init_app(app)  # Подключаем JWT к приложению

    # Регистрация роутов
    from src.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    from src.routes.history import history_bp
    app.register_blueprint(history_bp, url_prefix='/api/history')
    from src.routes.templates import templates_bp
    app.register_blueprint(templates_bp, url_prefix='/api/templates')
    return app