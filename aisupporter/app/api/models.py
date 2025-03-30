from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# 사용자 로더
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# 사용자 모델
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 농업 데이터 참조 모델 (실제 데이터는 Parquet 파일에 저장)
class DataReference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_type = db.Column(db.String(20), index=True)  # 환경, 병해충, 생육 등
    region = db.Column(db.String(20), index=True)
    reference_date = db.Column(db.DateTime, index=True)
    file_path = db.Column(db.String(256))
    record_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DataReference {self.data_type} - {self.region} - {self.reference_date}>' 