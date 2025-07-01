from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.models import RequestHistory, db

history_bp = Blueprint('history', __name__)

@history_bp.route('', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    history = RequestHistory.query.filter_by(user_id=user_id).order_by(RequestHistory.created_at.desc()).all()
    
    return jsonify([{
        'id': item.id,
        'element_type': item.element_type,
        'language': item.language,
        'additional_info': item.additional_info,
        'test_type': item.test_type,
        'code': item.code,
        'response': item.response_text,
        'created_at': item.created_at.isoformat()
    } for item in history]), 200

@history_bp.route('/<int:record_id>', methods=['DELETE'])
@jwt_required()
def delete_history_record(record_id):
    user_id = get_jwt_identity()
    record = RequestHistory.query.filter_by(id=record_id, user_id=user_id).first()
    
    if not record:
        return jsonify({"error": "Record not found"}), 404
        
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({"message": "Record deleted"}), 200

@history_bp.route('', methods=['POST'])
@jwt_required()
def save_history():
    user_id = get_jwt_identity()
    data = request.json
    
    # Валидация
    required_fields = ['element_type', 'language', 'test_type', 'code', 'response_text']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        new_record = RequestHistory(
            user_id=user_id,
            element_type=data['element_type'],
            language=data['language'],
            additional_info=data.get('additional_info', ''),
            test_type=data['test_type'],
            code=data['code'],
            response_text=data['response_text']
        )
        
        db.session.add(new_record)
        db.session.commit()
        
        return jsonify({
            "message": "History record saved",
            "record_id": new_record.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500