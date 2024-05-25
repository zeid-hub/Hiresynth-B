import requests
import json
from app import app, db
from models import User, Topic, SubjectiveQuestion, MultipleOption, Option, CodeChallenge, CodeExecution
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

def seed_topics():
    with app.app_context():  # Enter Flask application context
        # Clear existing topic data
        Topic.query.delete()
        db.session.commit()

        # Create Problem-solving Skills topic
        problem_solving_topic = Topic(name="Problem-solving Skills")
        db.session.add(problem_solving_topic)

        # Create Software Architecture and Design topic
        architecture_design_topic = Topic(name="Software Architecture and Design")
        db.session.add(architecture_design_topic)

        # Commit changes
        db.session.commit()
        
        print("Topics model populated successfully.")

def seed_subjective_questions():
    with app.app_context():  # Enter Flask application context
        # Clear existing subjective question data
        SubjectiveQuestion.query.delete()
        db.session.commit()

        # Get topics
        problem_solving_topic = Topic.query.filter_by(name="Problem-solving Skills").first()
        architecture_design_topic = Topic.query.filter_by(name="Software Architecture and Design").first()

        # Populate Problem-solving Skills questions
        problem_solving_questions = [
            "Describe a situation where the company's website experiences frequent crashes during peak traffic hours. How would you approach diagnosing and resolving this issue?",
            "A critical database query in the application is causing performance degradation. Provide steps to identify the bottleneck and optimize the query for better performance.",
            "You're tasked with designing a scalable messaging service similar to Slack. Discuss the key components and architectural decisions you would consider to ensure high performance and reliability.",
            "Given a large dataset of user records, propose an algorithm to efficiently find duplicate entries. Explain the time and space complexity of your approach.",
            "Compare and contrast the advantages and disadvantages of using a relational database versus a NoSQL database for a social media platform with millions of users. How would you decide which one to use?"
        ]
        for question_text in problem_solving_questions:
            question = SubjectiveQuestion(question_text=question_text, topic=problem_solving_topic)
            db.session.add(question)

        # Populate Software Architecture and Design questions
        architecture_design_questions = [
            "Compare and contrast the Model-View-Controller (MVC) and Microservices architectural patterns. When would you choose one over the other for building a web application, considering factors like scalability and maintainability?",
            "You're tasked with designing a ride-sharing service similar to Uber. Describe the key components, their interactions, and the database schema you would use to support this system.",
            "Discuss how you would design a backend system capable of handling millions of concurrent requests. What technologies, frameworks, and architectural decisions would you consider to ensure scalability and fault tolerance?",
            "Outline the database schema for a social media platform like Facebook, including entities like users, posts, comments, and relationships between them. Discuss the trade-offs between normalization and denormalization in this context.",
            "Describe the principles of designing RESTful APIs. How would you ensure consistency, scalability, and versioning in API design, considering the evolving needs of a software project?"
        ]
        for question_text in architecture_design_questions:
            question = SubjectiveQuestion(question_text=question_text, topic=architecture_design_topic)
            db.session.add(question)

        # Commit changes
        db.session.commit()
        
        print("Subjective questions model populated successfully.")

def seed_multiple_option_questions():
    with app.app_context():  # Enter Flask application context
        # Clear existing multiple option question data
        MultipleOption.query.delete()
        db.session.commit()

        # Get topics
        problem_solving_topic = Topic.query.filter_by(name="Problem-solving Skills").first()
        architecture_design_topic = Topic.query.filter_by(name="Software Architecture and Design").first()

        # Populate Problem-solving Skills questions and options
        problem_solving_questions = [
            {
                "question_text": "Which of the following is the most effective first step when diagnosing a performance issue in a web application?",
                "options": [
                    {"option_text": "Rewrite the entire application code"},
                    {"option_text": "Identify and isolate the specific part of the application causing the issue"},
                    {"option_text": "Increase the server resources without further investigation"}
                ],
                "correct_option_index": 1  # Index of the correct option in the options list
            },
            {
                "question_text": "When optimizing a slow database query, which approach is generally the best to start with?",
                "options": [
                    {"option_text": "Adding more indexes to the database tables"},
                    {"option_text": "Rewriting the application to use a different database system"},
                    {"option_text": "Analyzing the query execution plan to identify bottlenecks"}
                ],
                "correct_option_index": 2
            },
            {
                "question_text": "If a software application needs to handle a sudden spike in traffic, which strategy is most appropriate?",
                "options": [
                    {"option_text": "Deploying additional application instances and load balancing"},
                    {"option_text": "Upgrading all user devices to the latest hardware"},
                    {"option_text": "Rewriting the application in a different programming language"}
                ],
                "correct_option_index": 0
            },
            {
                "question_text": "When faced with a complex algorithmic problem, what is the best approach to take?",
                "options": [
                    {"option_text": "Write code immediately to solve the problem"},
                    {"option_text": "Break down the problem into smaller, manageable parts"},
                    {"option_text": "Ignore the problem and hope it resolves itself"}
                ],
                "correct_option_index": 1
            },
            {
                "question_text": "To ensure data integrity when multiple users access and modify the same record concurrently, which technique should be used?",
                "options": [
                    {"option_text": "Implementing optimistic concurrency control"},
                    {"option_text": "Allowing all changes to overwrite each other"},
                    {"option_text": "Disabling concurrent access to the application"}
                ],
                "correct_option_index": 0
            }
        ]

        # Populate Problem-solving Skills questions and options
        for question_data in problem_solving_questions:
            question = MultipleOption(question_text=question_data["question_text"], topic=problem_solving_topic)
            db.session.add(question)
            db.session.commit()  # Commit the question to generate its ID
            correct_option_index = question_data["correct_option_index"]
            options = question_data["options"]
            correct_option_id = None  # Initialize correct_option_id
            for option_data in options:
                option = Option(option_text=option_data["option_text"], multiple_question_id=question.id)
                db.session.add(option)
                if options.index(option_data) == correct_option_index:
                    correct_option_id = option.id

            # Set the correct_option_id outside the loop
            question.correct_option_id = correct_option_id
            # Commit the session inside the loop after each question
            db.session.commit()

        # Populate Software Architecture and Design questions and options
        architecture_design_questions = [
            {
                "question_text": "Which architectural pattern is best suited for developing a scalable web application that requires independent deployment of different services?",
                "options": [
                    {"option_text": "Monolithic Architecture"},
                    {"option_text": "Microservices Architecture"},
                    {"option_text": "Layered Architecture"}
                ],
                "correct_option_index": 1
            },
            {
                "question_text": "When designing a high-availability system, which of the following strategies is most effective?",
                "options": [
                    {"option_text": "Single point of failure"},
                    {"option_text": "Redundant components and failover mechanisms"},
                    {"option_text": "Minimal monitoring and logging"}
                ],
                "correct_option_index": 1
            },
            {
                "question_text": "What is a key benefit of using a RESTful API design for your web services?",
                "options": [
                    {"option_text": "Tight coupling between client and server"},
                    {"option_text": "Statelessness, which allows each request to be processed independently"},
                    {"option_text": "Mandatory session state on the server"}
                ],
                "correct_option_index": 1
            },
            {
                "question_text": "In a distributed system, how would you handle service discovery to manage the dynamic nature of service instances?",
                "options": [
                    {"option_text": "Hardcoding service locations in the client application"},
                    {"option_text": "Using a service registry and discovery mechanism like Consul or Eureka"},
                    {"option_text": "Manually updating service configurations"}
                ],
                "correct_option_index": 1
            },
            {
                "question_text": "Which of the following best describes the purpose of using design patterns in software development?",
                "options": [
                    {"option_text": "To enforce a specific coding style"},
                    {"option_text": "To provide reusable solutions to common problems"},
                                        {"option_text": "To write more complex code"}
                ],
                "correct_option_index": 1
            }
        ]

        # Populate Software Architecture and Design questions and options
        for question_data in architecture_design_questions:
            question = MultipleOption(question_text=question_data["question_text"], topic=architecture_design_topic)
            db.session.add(question)
            db.session.commit()  # Commit the question to generate its ID
            correct_option_index = question_data["correct_option_index"]
            options = question_data["options"]
            correct_option_id = None  # Initialize correct_option_id
            for option_data in options:
                option = Option(option_text=option_data["option_text"], multiple_question_id=question.id)
                db.session.add(option)
                if options.index(option_data) == correct_option_index:
                    correct_option_id = option.id

            # Set the correct_option_id outside the loop
            question.correct_option_id = correct_option_id
            # Commit the session inside the loop after each question
            db.session.commit()

        print("Multiple option questions model populated successfully.")

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
    # Seed users
    seed_users()

    # Call the seed_topics function
    seed_topics()

    # Call the seed_subjective_questions function
    seed_subjective_questions()

    # Call the seed_multiple_option_questions function
    seed_multiple_option_questions()

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

    # seed_sample_user_codes()