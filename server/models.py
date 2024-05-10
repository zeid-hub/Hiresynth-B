from datetime import datetime
from config import db  # Import db from config.py

class TestSession(db.Model):
    __tablename__ = 'test_sessions'

    id = db.Column(db.Integer, primary_key=True)
    time_taken = db.Column(db.Integer, nullable=False)  # Time taken by the user to complete the test
    submitted_answers = db.Column(db.Integer, nullable=False)  # Number of submitted answers
    submitted_at = db.Column(db.DateTime, default=datetime.now, nullable=False)  # Timestamp when the test was submitted
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    #relationship with Assessment model
    assessments = db.relationship("Assessment", back_populates="test_session")

    #relationship with User model
    users = db.relationship("User", back_populates="test_session")
    
    
    def __repr__(self):
        return f"<TestSession id={self.id}, time_taken={self.time_taken}, submitted_answers={self.submitted_answers}, submitted_at={self.submitted_at}>"

class AssessmentScore(db.Model):
    __tablename__ = 'assessment_scores'

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, nullable=False)
    completion_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    assessment = db.relationship("Assessment", back_populates="assessment_scores")
    user = db.relationship("User", back_populates="assessment_scores")

    
    def __repr__(self):
        return f"<AssessmentScore id={self.id}, score={self.score}, completion_date={self.completion_date}>"
