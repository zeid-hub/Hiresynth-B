from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'multiple choice', 'subjective', 'coding challenge'
    time_limit = db.Column(db.Integer) 
    status = db.Column(db.String(50), nullable=False, default='draft')  # 'draft' or 'published'

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populate="assessments")

    # Representation
    def __repr__(self):
        return f"<Assessment {self.title}>"
    
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'multiple choice', 'subjective'

    # Additional fields (if needed)
    options = db.Column(db.JSON)  # JSON field to store options for multiple choice questions
    correct_answer = db.Column(db.String(255))  # For multiple choice questions, store the correct answer

    # Relationships
    assessment = db.relationship('Assessment', back_populates='questions')

    # Representation
    def __repr__(self):
        return f"<Question {self.text}>"
