from src.app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    requests = db.relationship('RequestHistory', backref='user', lazy=True, cascade='all, delete-orphan' )
    templates = db.relationship('Templates', backref='user', lazy=True, cascade='all, delete-orphan' )
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }

class RequestHistory(db.Model):
    __tablename__ = 'request_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    element_type = db.Column(db.String(50), nullable=False)  
    language = db.Column(db.String(50), nullable=False)      
    additional_info = db.Column(db.Text)                     
    test_type = db.Column(db.String(100), nullable=False)    
    code = db.Column(db.Text, nullable=False)                
    response_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Templates(db.Model):
    __tablename__ = 'templates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    element_type = db.Column(db.String(50), nullable=False)  
    language = db.Column(db.String(50), nullable=False)      
    additional_info = db.Column(db.Text)                     
    test_type = db.Column(db.String(100), nullable=False)    
    code = db.Column(db.Text, nullable=False)                
    created_at = db.Column(db.DateTime, default=datetime.utcnow)