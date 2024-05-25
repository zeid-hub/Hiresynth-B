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
    
   
# class SubjectiveQuestion(db.Model):
#     __tablename__ = 'subjectivequestions'

#     id = db.Column(db.Integer, primary_key=True)
#     question_text = db.Column(db.Text, nullable=False)
#     maximum_length = db.Column(db.Integer)  # Maximum character limit for the response
#     required = db.Column(db.Boolean, default=True)  # Whether the question is mandatory or optional

#     topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
#     topic = db.relationship('Topic', backref='subjectivequestions')
    
#     def __repr__(self):
#         return f"<SubjectiveQuestion {self.id}: {self.question_text}>"

# class Topic(db.Model):
#     __tablename__ = 'topics'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(), nullable=False, unique=True)

#     def __repr__(self):
#         return f"<Topic {self.name}>"

# class MultipleOption(db.Model):
#     __tablename__ = 'multiple_questions'

#     id = db.Column(db.Integer, primary_key=True)
#     question_text = db.Column(db.Text, nullable=False)
#     correct_option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=True)
#     topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)

#     topic = db.relationship('Topic', backref='multiple_questions')
#     options = db.relationship('Option', backref='multiple_question', foreign_keys=[correct_option_id])

#     def __repr__(self):
#         return f"<MultipleQuestion {self.id}: {self.question_text}>"

#     @property
#     def has_three_options(self):
#         return len(self.options) == 3

# class Option(db.Model):
#     __tablename__ = 'options'

#     id = db.Column(db.Integer, primary_key=True)
#     option_text = db.Column(db.Text, nullable=False)
#     multiple_question_id = db.Column(db.Integer, db.ForeignKey('multiple_questions.id'), nullable=False)

#     def __repr__(self):
#         return f"<Option {self.id}: {self.option_text}>"
    
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
