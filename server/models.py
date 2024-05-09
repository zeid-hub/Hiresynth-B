from config import db, bcrypt
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
    assessment = db.relationship("Assessment", back_populates = "user")

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
    options = db.Column(db.JSON) 
    correct_answer = db.Column(db.String(255)) 

    # Relationships
    assessment = db.relationship('Assessment', back_populates='questions')
