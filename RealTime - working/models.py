from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"

    email = db.Column(db.String(120), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # Uses scrypt

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.email  # Use email as the unique identifier
