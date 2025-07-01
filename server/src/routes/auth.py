from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from src.models import User, db
from sqlalchemy import text
from src.app import jwt 

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    #Требуемые поля
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Хеширование пароля
    hashed_password = generate_password_hash(data['password'])
    
    # Создание пользователя
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hashed_password 
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password_hash, data['password']):
        # Преобразуем ID пользователя в строку
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()  # Теперь функция доступна
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200

@auth_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Проверка пароля для подтверждения
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({"error": "Password is required"}), 400
    
    if not check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Invalid password"}), 401
    
    # Удаление пользователя и всех связанных записей
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "Account and all related data deleted"}), 200