from config import db

class Invitation(db.Model):
    __tablename__ = 'invitations'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50))
    time = db.Column(db.DateTime, default=db.func.now())
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship("User", back_populates="invitations")

    def __repr__(self):
        return f"<Invitation(id={self.id}, status={self.status}, time={self.time})>"

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    feedback_text = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Establishing the one-to-many relationship with Feedback model
    user = db.relationship("User", back_populates="feedbacks")

    def __repr__(self):
        return f"<Feedback(id={self.id}, feedback_text={self.feedback_text})>"
    