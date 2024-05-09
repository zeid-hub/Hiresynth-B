from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # either recruiter or interviewee

    # Additional fields
    username = db.Column(db.String(100))

    # Constructor
    def __init__(self, email, password, role, username=None):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role
        self.username = username

    # Password hashing
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Representation
    def __repr__(self):
        return f"<User {self.email}>"

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'multiple choice', 'subjective', 'coding challenge'
    time_limit = db.Column(db.Integer)  # Assuming time limit is in minutes
    status = db.Column(db.String(50), nullable=False, default='draft')  # 'draft' or 'published'

    # Relationships
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creator = relationship('User', backref='assessments')

    # Constructor
    def __init__(self, title, description, type, creator_id, time_limit=None, status='draft'):
        self.title = title
        self.description = description
        self.type = type
        self.creator_id = creator_id
        self.time_limit = time_limit
        self.status = status

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
    assessment = relationship('Assessment', backref='questions')

    # Constructor
    def __init__(self, assessment_id, text, type, options=None, correct_answer=None):
        self.assessment_id = assessment_id
        self.text = text
        self.type = type
        self.options = options
        self.correct_answer = correct_answer

    # Representation
    def __repr__(self):
        return f"<Question {self.text}>"
