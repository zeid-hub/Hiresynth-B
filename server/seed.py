from app import app, db
from models import User, CodeExecution

def seed_sample_user_codes():
    with app.app_context():
        # Clear existing code storage data
        CodeExecution.query.delete()
        db.session.commit()
        
        # Query user objects from the database
        recruiters = User.query.filter_by(role='Recruiter').all()
        interviewees = User.query.filter_by(role='Interviewee').all()
        
        if not recruiters:
            print("Error: No Recruiters found.")
            return
        if not interviewees:
            print("Error: No Interviewees found.")
            return

        user_codes = [
            "def add(a, b):\n    return a + b",
            "def subtract(a, b):\n    return a - b",
            "def multiply(a, b):\n    return a * b",
            "def divide(a, b):\n    return a / b"
        ]

        # Assign each code to a different recruiter and interviewee
        for i, recruiter in enumerate(recruiters):
            code_execution_recruiter = CodeExecution(user_id=recruiter.id, user_code=user_codes[i % len(user_codes)], language="python")
            db.session.add(code_execution_recruiter)

        for i, interviewee in enumerate(interviewees):
            code_execution_interviewee = CodeExecution(user_id=interviewee.id, user_code=user_codes[(i + len(recruiters)) % len(user_codes)], language="python")
            db.session.add(code_execution_interviewee)

        db.session.commit()

        print("Sample user codes seeded successfully.")


if __name__ == '__main__':
    
    # Call the seed_sample_user_codes function
    seed_sample_user_codes()
    
    

   