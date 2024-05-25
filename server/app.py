# from config import app, bcrypt,  get_jwt_identity
from config import app, db, request, make_response, api, Resource, jsonify
from models import db, CodeChallenge, CodeExecution, AssessmentScore
from datetime import datetime
import subprocess
import bleach

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
                    "language": code_execution.language,
                    "timer": code_execution.timer.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime to string
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
                    'language': code_execution.language,
                    'timer': code_execution.timer.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime to string
                }, 200
            else:
                return {'message': 'Code execution not found'}, 404

    def post(self):
        data = request.json

        user_code = data.get('user_code')
        language = data.get('language')
        timer_str = data.get('timer')  # Extract timer as string from request payload
        user_id = data.get('user_id')
        
        if not user_code or not user_code.strip():
            return {'message': 'User code cannot be empty'}, 400
        
        sanitized_user_code = bleach.clean(user_code)
        
        # Convert timer string to datetime object
        try:
            timer = datetime.strptime(timer_str, "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError as e:
            return {'message': f'Error parsing timer string: {str(e)}'}, 400
        
        code_execution = CodeExecution(
            user_code=sanitized_user_code,
            language=language,
            timer=timer,
            user_id=user_id
        )
        db.session.add(code_execution)
        db.session.commit()
        
        return {'message': 'Code submitted successfully'}, 201

api.add_resource(CodeExecutionResource, '/code_execution', '/code_execution/<int:code_execution_id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)