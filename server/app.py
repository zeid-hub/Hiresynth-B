from flask_cors import CORS
from config import app, db, request, make_response, api, Resource, jsonify, jwt, create_access_token, jwt_required, current_user, get_jwt, set_access_cookies
from models import db, User, MultipleOption, CodeChallenge, SubjectiveQuestion, Topic, TokenBlocklist
import datetime
from datetime import timedelta, timezone
CORS(app)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(username=identity).one_or_none()

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

class Home (Resource):
    @jwt_required()
    def get(self):
        print(current_user.username, current_user.email, current_user._password_hash, current_user.id)
        response = (
            {
                "Message": "Welcome to my Home Page"
            }
        )
        return make_response(
            response,
            200
        )
api.add_resource(Home, "/")

class AddUser(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        role = data.get('role')
        password = data.get('password')

        if not username or not email or not role or not password:
            return jsonify({"error": "Username, email, role and password are required."}), 400

        new_user = User(username=username, email=email, role=role)
        new_user.password_hash = password
        db.session.add(new_user)
        db.session.commit()
        
        return make_response({"message": "The user has been created successfully"}, 201)

api.add_resource(AddUser, "/adduser")


class GetAllUsers(Resource):
    def get(self):
        users = User.query.all()
        user_list = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
            for user in users
        ]
        response = make_response(jsonify(user_list), 200)
        return response

api.add_resource(GetAllUsers, "/getallusers")

class LoginUser(Resource):
    def post(self):
        data = request.get_json()

        new_user = User.query.filter_by(email=data['email']).first()
        if not new_user:
            return jsonify({"error": "email is incorrect."}), 400

        if new_user.validates(data['password']):
            given_token = create_access_token(identity=new_user.username)
            return make_response(
                jsonify(
                    {"message": "The user has been logged in successfully", "token": given_token}
                    ),
                    200
            )
        else:
            return make_response(
                jsonify(
                    {"error": "You have entered the Incorrect password"}
                ),
                400
            )

api.add_resource(LoginUser, "/login")

class LogoutUser(Resource):
    @jwt_required
    def delete(self):
        jti = get_jwt()["jti"]
        now = datetime.now(timezone.utc)
        token = TokenBlocklist(jti=jti, created_at=now)
        db.session.add(token)
        db.session.commit()
        return make_response(
            jsonify(
                {"message": "Successfully logged out"}
            ),
            200
        )
api.add_resource(LogoutUser, "/logout")

# API endpoint to update password
@app.route('/update_password', methods=['POST'])
def update_password():
    data = request.get_json()

    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    username = data.get('username')  # Use username instead of userId

    user = User.query.filter_by(username=username).first()  # Retrieve user by username
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.validates(old_password):
        return jsonify({'message': 'Old password is incorrect'}), 400

    user.password_hash = new_password

    db.session.commit()

    return jsonify({'message': 'Password updated successfully'}), 200

@app.route('/questions/all')
def all_questions():
    all_questions = []

    subjective_questions = SubjectiveQuestion.query.all()
    all_questions.extend(subjective_questions)

    multiple_choice_questions = MultipleOption.query.all()
    all_questions.extend(multiple_choice_questions)

    code_challenges = CodeChallenge.query.all()
    all_questions.extend(code_challenges)

    serialized_questions = []
    for question in all_questions:
        if isinstance(question, SubjectiveQuestion):
            serialized_question = {
                'type': 'subjective',
                'id': question.id,
                'question_text': question.question_text
            }
        elif isinstance(question, MultipleOption):
            serialized_question = {
                'type': 'multiple_choice',
                'id': question.id,
                'question_text': question.question_text
            }
        elif isinstance(question, CodeChallenge):
            serialized_question = {
                'type': 'code_challenge',
                'id': question.id,
                'title': question.title
            }
        serialized_questions.append(serialized_question)

    return jsonify(questions=serialized_questions)

@app.route('/code_challenges', methods=['GET'])
def get_code_challenges():
    challenges = CodeChallenge.query.all()
    challenges_list = [
        {
            'id': challenge.id,
            'title': challenge.title,
            'description': challenge.description,
            'languages': challenge.languages,
            'correct_answer': challenge.correct_answer,
        } for challenge in challenges
    ]
    return jsonify(challenges_list)

@app.route('/code_challenges/<int:id>', methods=['GET'])
def get_code_challenge(id):
    challenge = CodeChallenge.query.get_or_404(id)
    return jsonify({
        'id': challenge.id,
        'title': challenge.title,
        'description': challenge.description,
        'languages': challenge.languages
    })

@app.route('/code_challenges', methods=['POST'])
def create_code_challenge():
    data = request.get_json()
    new_challenge = CodeChallenge(
        title=data['title'],
        description=data['description'],
        languages=data['languages'],
        correct_answer=data['correct_answer']
    )
    db.session.add(new_challenge)
    db.session.commit()
    return jsonify({
        'id': new_challenge.id,
        'title': new_challenge.title,
        'description': new_challenge.description,
        'languages': new_challenge.languages
    }), 201

@app.route('/code_challenges/<int:id>', methods=['PATCH'])
def update_code_challenge(id):
    challenge = CodeChallenge.query.get_or_404(id)
    data = request.get_json()
    if 'title' in data:
        challenge.title = data['title']
    if 'description' in data:
        challenge.description = data['description']
    if 'languages' in data:
        challenge.languages = data['languages']
    if 'correct_answer' in data:
        challenge.correct_answer = data['correct_answer']
    db.session.commit()
    return jsonify({
        'id': challenge.id,
        'title': challenge.title,
        'description': challenge.description,
        'languages': challenge.languages
    })

@app.route('/code_challenges/<int:id>', methods=['DELETE'])
def delete_code_challenge(id):
    challenge = CodeChallenge.query.get_or_404(id)
    db.session.delete(challenge)
    db.session.commit()
    return jsonify({'message': 'Code challenge deleted successfully'}), 204

@app.route('/subjective_questions_per_topic', methods=['GET'])
def get_subjective_questions_per_topic():
    topics = Topic.query.all()
    topic_subjective_questions = []

    for topic in topics:
        topic_data = {
            'topic_id': topic.id,
            'topic_name': topic.name,
            'subjective_questions': []
        }

        questions = SubjectiveQuestion.query.filter_by(topic_id=topic.id).all()

        for question in questions:
            question_data = {
                'question_id': question.id,
                'question_text': question.question_text,
                'maximum_length': question.maximum_length,
                'required': question.required
            }
            topic_data['subjective_questions'].append(question_data)

        topic_subjective_questions.append(topic_data)

    return jsonify({'topics_with_subjective_questions': topic_subjective_questions})

@app.route('/subjective_questions/<int:topic_id>', methods=['GET'])
def get_subjective_questions_by_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    questions = SubjectiveQuestion.query.filter_by(topic_id=topic.id).all()

    topic_data = {
        'topic_id': topic.id,
        'topic_name': topic.name,
        'subjective_questions': []
    }

    for question in questions:
        question_data = {
            'question_id': question.id,
            'question_text': question.question_text,
            'maximum_length': question.maximum_length,
            'required': question.required
        }
        topic_data['subjective_questions'].append(question_data)

    return jsonify(topic_data)

@app.route('/subjective_questions', methods=['POST'])
def create_subjective_question():
    data = request.json
    topic_id = data.get('topic_id')
    topic = Topic.query.get_or_404(topic_id)
    
    new_question = SubjectiveQuestion(
        question_text=data['question_text'],
        maximum_length=data['maximum_length'],
        required=data['required'],
        topic=topic
    )
    
    db.session.add(new_question)
    db.session.commit()
    
    return jsonify({'message': 'Subjective question created successfully'}), 201

@app.route('/subjective_questions/<int:question_id>', methods=['PATCH'])
def update_subjective_question(question_id):
    question = SubjectiveQuestion.query.get_or_404(question_id)
    data = request.json
    
    if 'question_text' in data:
        question.question_text = data['question_text']
    if 'maximum_length' in data:
        question.maximum_length = data['maximum_length']
    if 'required' in data:
        question.required = data['required']
    
    db.session.commit()
    
    return jsonify({'message': 'Subjective question updated successfully'})

@app.route('/subjective_questions/<int:question_id>', methods=['DELETE'])
def delete_subjective_question(question_id):
    question = SubjectiveQuestion.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'message': 'Subjective question deleted successfully'})


if __name__ == '__main__':
    app.run(port=5555, debug=True)