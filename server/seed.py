import requests
import json
from app import app, db
# from models import User, Topic, SubjectiveQuestion, MultipleOption, Option, CodeChallenge
from models import User, CodeChallenge
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def seed_users(num_recruiters=5, num_interviewees=10):
    with app.app_context():  # Enter Flask application context
        # Clear existing user data
        User.query.delete()
        db.session.commit()

        # Create Recruiter users
        for _ in range(num_recruiters):
            username = fake.user_name()
            email = fake.email()
            password = fake.password(length=10)  # Generate a random password
            recruiter = User(username=username, role='Recruiter', email=email, password_hash=password)
            db.session.add(recruiter)

        # Create Interviewee users
        for _ in range(num_interviewees):
            username = fake.user_name()
            email = fake.email()
            password = fake.password(length=10)  # Generate a random password
            interviewee = User(username=username, role='Interviewee', email=email, password_hash=password)
            db.session.add(interviewee)

        # Commit changes
        db.session.commit()
        
        print(f"Users model populated successfully with {num_recruiters} recruiters and {num_interviewees} interviewees.")

def populate_CodeChallenge_from_api(challenge_ids_or_slugs, correct_answers):
    with app.app_context():
        # Clear existing assessment data
        CodeChallenge.query.delete()
        db.session.commit()

        # Fixed list of languages
        fixed_languages = ['python', 'javascript', 'ruby']  # Fixed the order to match correct_answers keys

        for language in fixed_languages:
            for challenge_id_or_slug in challenge_ids_or_slugs:
                api_url = f"https://www.codewars.com/api/v1/code-challenges/{challenge_id_or_slug}"
                response = requests.get(api_url)

                if response.status_code == 200:
                    data = response.json()
                    # Extracting data from API response
                    title = data['name']
                    description = data['description']

                    # Retrieve the correct answer from the correct_answers dictionary
                    correct_answer = ""
                    if title in correct_answers:
                        if language in correct_answers[title]:
                            correct_answer = json.dumps(correct_answers[title][language])
                        else:
                            print(f"Warning: No answer found for challenge '{title}' in language '{language}'.")
                    else:
                        print(f"Warning: Challenge '{title}' not found in 'correct_answers' dictionary.")

                    # Create CodeChallenge instance and add to session
                    challenge = CodeChallenge(
                        title=title,
                        description=description,
                        languages=json.dumps([language]),  # Single language
                        correct_answer=correct_answer
                    )

                    db.session.add(challenge)

            # Commit the session after each language iteration
            db.session.commit()

        print("CodeChallenges seeded successfully.")




if __name__ == '__main__':
    
    seed_users()

    correct_answers = {
    "Does my number look big in this?": {
        "python": ["true", "true", "false", "false"],
        "javascript": ["true", "true", "false", "false"],
        "ruby": ["true", "true", "false", "false"]
    },
    "Sort the Gift Code": {
        "python": ["abcdef", "kpqsuvy", "abcdefghijklmnopqrstuvwxyz"],
        "javascript": ["abcdef", "kpqsuvy", "abcdefghijklmnopqrstuvwxyz"],
        "ruby": ["abcdef", "kpqsuvy", "abcdefghijklmnopqrstuvwxyz"]
    },
    "Don't give me five!": {
        "python": [8, 12],
        "javascript": [8, 12],
        "ruby": [8, 12]
    },
    "Even or Odd": {
        "python": ["Odd", "Even", "Odd", "Even", "Even"],
        "javascript": ["Odd", "Even", "Odd", "Even", "Even"],
        "ruby": ["Odd", "Even", "Odd", "Even", "Even"]
    },
    "Who likes it?": {
        "python": ["no one likes this", "Peter likes this", "Jacob and Alex like this", "Max, John and Mark like this", "Alex, Jacob and 2 others like this"],
        "javascript": ["no one likes this", "Peter likes this", "Jacob and Alex like this", "Max, John and Mark like this", "Alex, Jacob and 2 others like this"],
        "ruby": ["no one likes this", "Peter likes this", "Jacob and Alex like this", "Max, John and Mark like this", "Alex, Jacob and 2 others like this"]
    },
    "Allocating Hotel Rooms": {
        "python": [[1, 2, 1], [1, 2, 1, 2], [1, 2, 2, 3, 2], [1, 2, 2, 3, 4, 1, 3, 2], [4, 1, 5, 1, 2, 4, 2, 3, 3, 3], "None"],
        "javascript": [[1, 2, 1], [1, 2, 1, 2], [1, 2, 2, 3, 2], [1, 2, 2, 3, 4, 1, 3, 2], [4, 1, 5, 1, 2, 4, 2, 3, 3, 3], "null"],
        "ruby": [[1, 2, 1], [1, 2, 1, 2], [1, 2, 2, 3, 2], [1, 2, 2, 3, 4, 1, 3, 2], [4, 1, 5, 1, 2, 4, 2, 3, 3, 3], "nil"]
    },
    "Reversed Strings": {
        "python": ['dlrow', 'olleh', '', 'h'],
        "javascript": ['dlrow', 'olleh', '', 'h'],
        "ruby": ['dlrow', 'olleh', '', 'h']
    },
    "Shortest steps to a number": {
        "python": [0, 4, 4, 9],
        "javascript": [0, 4, 4, 9],
        "ruby": [0, 4, 4, 9]
    },
    "Bit Counting": {
        "python": [0, 1, 3, 2, 2],
        "javascript": [0, 1, 3, 2, 2],
        "ruby": [0, 1, 3, 2, 2]
    },
    "Persistent Bugger.": {
        "python": [3, 0, 2, 4],
        "javascript": [3, 0, 2, 4],
        "ruby": [3, 0, 2, 4]
    }
}

    # Seed assessments from API
    populate_CodeChallenge_from_api(["does-my-number-look-big-in-this", "sort-the-gift-code", "dont-give-me-five", "even-or-odd", "who-likes-it", "allocating-hotel-rooms", "reversed-strings", "shortest-steps-to-a-number", "bit-counting", "persistent-bugger"], correct_answers)