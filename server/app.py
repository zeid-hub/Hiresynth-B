from flask import request
from flask_cors import CORS
from config import app, db, request, make_response, api, Resource, jsonify, jwt, create_access_token, jwt_required, current_user, get_jwt, set_access_cookies
from models import db, User, CodeChallenge, TokenBlocklist, AssessmentScore, CodeExecution, CreditCard, CodeResult
# import datetime
from datetime import timedelta, timezone, datetime
import subprocess
import bleach

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
        print(data)
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

class Execution(Resource):
    def post(self):
        payload = request.json
        question_title = payload.get('question_title')
        language = payload.get('language')
        user_code = payload.get('code', "")
        interviewee_id = payload.get('user_id')

        # Fetch the code challenge based on the question title
        code_challenge = CodeChallenge.query.filter_by(title=question_title).first()

        # Initialize a dictionary to store results for the question
        question_results = {}

        if code_challenge:
            # Retrieve the expected outputs from the code challenge
            expected_outputs = code_challenge.correct_answer

            # Execute the user code against the code challenge
            output = self.execute_code(language, user_code)

            # Check if the actual output matches any of the expected outputs
            passed = output in expected_outputs

            # Generate error message if the answer is incorrect
            error_message = None
            if not passed:
                error_message = f"Incorrect answer: Expected one of {expected_outputs}, but got {output}."
                
            # Append the question result to the question results list
            question_results[question_title] = [{
                'expected_output': expected_outputs,
                'result': output,
                'passed': passed,
                'error_message': error_message
            }]

            # Calculate overall score
            overall_score = 1 if passed else 0

            # Store the assessment score in the database associated with the interviewee
            assessment_score = AssessmentScore(score=overall_score, user_id=interviewee_id)
            db.session.add(assessment_score)
            db.session.commit()

            # Send the results along with the assessment score to the frontend
            return make_response(jsonify({'results': question_results, 'assessment_score': overall_score}), 200)
        else:
            return {'message': 'Code challenge not found'}, 404

    def execute_code(self, language, user_code):
        try:
            if language.lower() == 'python':
                exec_code = f"""
import json

def run_user_code():
    {user_code}
    function_name = [name for name in globals() if callable(globals()[name]) and name not in dir(__builtins__)]
    if function_name:
        result = globals()[function_name[0]]()
        print(result)

run_user_code()
"""
                result = subprocess.run(
                    ['python', '-c', exec_code],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            elif language.lower() == 'ruby':
                exec_code = f"""
def run_user_code()
    {user_code}
    function_name = local_variables.select {{ |name| eval(name.to_s).is_a?(Method) }}.first
    if function_name
        result = send(function_name)
        puts result
    end
end

run_user_code()
"""
                result = subprocess.run(
                    ['ruby', '-e', exec_code],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            elif language.lower() == 'javascript':
                exec_code = f"""
function runUserCode() {{
    {user_code}
    let functionName = Object.keys(this).find(key => typeof this[key] === 'function' && key !== 'runUserCode');
    if (functionName) {{
        let result = this[functionName]();
        if (typeof result !== 'undefined') {{
            console.log(result);
        }}
    }}
}}
runUserCode();
"""
                result = subprocess.run(
                    ['node', '-e', exec_code],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            else:
                return "Unsupported language."

            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "Code execution timed out."
        except Exception as e:
            return f"Error during code execution: {e}"

    def calculate_overall_score(self, question_results):
        # Calculate the overall score based on question results
        total_tests = len(question_results)
        total_passed = sum(result['passed'] for result in question_results)

        overall_score = total_passed / total_tests if total_tests > 0 else 0
        return overall_score

api.add_resource(Execution, '/execute_code')


class CodeExecutionResource(Resource):
    def get(self, code_execution_id=None):
        if code_execution_id is None:
            # Retrieve all code executions
            code_executions = CodeExecution.query.all()
            code_execution_list = [
                {
                    "id": code_execution.id,
                    "user_code": code_execution.user_code,
                    "code_output": code_execution.code_output,
                    "language": code_execution.language
                }
                for code_execution in code_executions
            ]
            return make_response(jsonify(code_execution_list), 200)
        else:
            # Retrieve a specific code execution by ID
            code_execution = CodeExecution.query.filter_by(id=code_execution_id).first()
            if code_execution:
                return {
                    'user_code': code_execution.user_code,
                    'code_output': code_execution.code_output,
                    'language': code_execution.language
                }, 200
            else:
                return {'message': 'Code execution not found'}, 404

    def post(self):
        data = request.json

        user_code = data.get('user_code')
        language = data.get('language')
        code_output = data.get('code_output')  # Extract code_output from request payload

        if not user_code or not user_code.strip():
            return {'message': 'User code cannot be empty'}, 400

        sanitized_user_code = bleach.clean(user_code)

        code_execution = CodeExecution(
            user_code=sanitized_user_code,
            code_output=code_output,  # Include code_output
            language=language
        )
        db.session.add(code_execution)
        db.session.commit()

        return {'message': 'Code submitted successfully'}, 201

api.add_resource(CodeExecutionResource, '/code_execution', '/code_execution/<int:code_execution_id>')


# Route to get all credit cards
@app.route('/credit_cards', methods=['GET'])
def get_credit_cards():
    # Retrieve all credit cards from the database
    credit_cards = CreditCard.query.all()
    # Serialize the credit cards to JSON
    credit_cards_json = [
        {
            'id': card.id,
            'card_number': card.card_number,
            'expiration_date': card.expiration_date,
            'cvv': card.cvv,
            'country': card.country,
            'city': card.city,
            'amount_transacted': card.amount_transacted
        } for card in credit_cards
    ]
    return jsonify(credit_cards_json), 200

# Route to add a new credit card
@app.route('/credit_cards', methods=['POST'])
def add_credit_card():
    # Extract data from the request
    data = request.json
    card_number = data.get('card_number')
    expiration_date = data.get('expiration_date')
    cvv = data.get('cvv')
    country = data.get('country')
    city = data.get('city')
    amount_transacted = data.get('amount_transacted', 0.0)  # Default to 0.0 if not provided

    # Create a new credit card instance
    new_card = CreditCard(
        card_number=card_number,
        expiration_date=expiration_date,
        cvv=cvv,
        country=country,
        city=city,
        amount_transacted=amount_transacted
    )

    # Add the new credit card to the database
    db.session.add(new_card)
    db.session.commit()

    return jsonify({
        'id': new_card.id,
        'card_number': new_card.card_number,
        'expiration_date': new_card.expiration_date,
        'cvv': new_card.cvv,
        'country': new_card.country,
        'city': new_card.city,
        'amount_transacted': new_card.amount_transacted
    }), 201

@app.route('/code_results', methods=['GET'])
def get_all_code_results():
    code_results = CodeResult.query.all()
    code_results_list = [
        {
            'id': code_result.id,
            'user_code': code_result.user_code,
            'code_output': code_result.code_output,
            'language': code_result.language,
            'question': code_result.question  # Include question in the response
        }
        for code_result in code_results
    ]
    return jsonify(code_results_list), 200


@app.route('/code_results', methods=['POST'])
def submit_code_result():
    data = request.json
    user_code = data.get('user_code')
    code_output = data.get('code_output')
    language = data.get('language')
    question = data.get('question')

    # Validate data if necessary

    # Fetch the corresponding code challenge
    code_challenge = CodeChallenge.query.filter_by(description=question).first()

    # Check the answer against the code challenge
    score = code_challenge.check_answer(code_output)

    # Save the code result to the database
    code_result = CodeResult(user_code=user_code, code_output=code_output, language=language, question=question)
    db.session.add(code_result)
    db.session.commit()

    # Determine pass or fail based on the score
    if score == 100:
        message = 'Congratulations! You passed the challenge.'
    else:
        message = 'Sorry, you failed the challenge.'

    return jsonify({'message': message, 'score': score}), 201

    
if __name__ == '__main__':
    app.run(port=5555, debug=True)