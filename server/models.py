from config import db, bcrypt
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    role = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    _password_hash = db.Column(db.String(), nullable=False)

    feedbacks = db.relationship("Feedback", back_populates="user")
    invitations = db.relationship("Invitation", back_populates="user")
    assessments = db.relationship("Assessment", back_populates="user")
    assessment_scores = db.relationship("AssessmentScore", back_populates="user") 
    test_session = db.relationship("TestSession", back_populates="users")
    code_executions = db.relationship("CodeExecution", back_populates="user")

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, my_password):
        self._password_hash = bcrypt.generate_password_hash(my_password).decode('utf-8')
        return self._password_hash

    def validates (self, my_password):
        return bcrypt.check_password_hash(self.password_hash, my_password)

    def __repr__(self):
        return f"<User {self.username}, {self.email}, {self._password_hash}>"

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

class Invitation(db.Model):
    __tablename__ = 'invitations'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    time = db.Column(db.DateTime, default=db.func.now())
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship("User", back_populates="invitations")

    def __repr__(self):
        return f"<Invitation(id={self.id}, status={self.status}, time={self.time})>"

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    feedback_text = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Establishing the one-to-many relationship with Feedback model
    user = db.relationship("User", back_populates="feedbacks")

    def __repr__(self):
        return f"<Feedback(id={self.id}, feedback_text={self.feedback_text})>"

class CodeChallenge(db.Model):
    __tablename__ = 'code_challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=False)
    languages = db.Column(db.String(), nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)  

    def __repr__(self):
        return f"<CodeChallenge {self.title}, Correct Answer: {self.correct_answer}, Languages: {self.languages}>"

    
class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'multiple choice', 'subjective', 'coding challenge'
    time_limit = db.Column(db.Integer) 
    status = db.Column(db.String(50), nullable=False, default='draft')  # 'draft' or 'published'

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship("User", back_populates="assessments")
    assessment_scores = db.relationship("AssessmentScore", back_populates = "assessment")
    test_session = db.relationship("TestSession", back_populates = "assessments")

    questions = db.relationship('Question', secondary='assessment_question', backref='assessments')

    def __repr__(self):
        return f"<Assessment {self.title}>"

# Association Table for Many-to-Many Relationship between Assessment and Question
assessment_question = db.Table('assessment_question',
    db.Column('assessment_id', db.Integer, db.ForeignKey('assessments.id'), primary_key=True),
    db.Column('question_id', db.Integer, db.ForeignKey('questions.id'), primary_key=True)
)

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'multiple choice', 'subjective'

    # Additional fields (if needed)
    options = db.Column(db.JSON) 
    correct_answer = db.Column(db.String(255)) 

    # Relationships
    assessment = db.relationship('Assessment', back_populates='questions')

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


class CodeExecution(db.Model):
    __tablename__ = 'code_executions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_code_executions_user_id'), nullable=False)  # Explicitly name the foreign key constraint
    user_code = db.Column(db.Text, nullable=False)
    code_output = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(), nullable=False)

    user = db.relationship('User', back_populates='code_executions')

    def __repr__(self):
        return f"<CodeExecution id={self.id}, user_id={self.user_id}>"


class CreditCard(db.Model):
    __tablename__ = 'credit_cards'

    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(16), nullable=False)  # Assuming a 16-digit card number
    expiration_date = db.Column(db.String(7), nullable=False)  # Format: MM/YYYY
    cvv = db.Column(db.String(3), nullable=False)  # Card Verification Value
    country = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(), nullable=False)
    amount_transacted = db.Column(db.Float, default=0.0)  # Amount transacted using this card

    def __repr__(self):
        return f"<CreditCard {self.card_number}, Expiry: {self.expiration_date}, CVV: {self.cvv}, Amount Transacted: {self.amount_transacted}>"


class CodeResult(db.Model):
    __tablename__ = 'code_results'

    id = db.Column(db.Integer, primary_key=True)
    user_code = db.Column(db.Text, nullable=False)
    code_output = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"<CodeResult id={self.id}>"